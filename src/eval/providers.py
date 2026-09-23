"""Text-only provider adapters. No implicit retries; keys stay in environment variables."""
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse, quote


class ProviderHTTPError(RuntimeError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"provider_http_{status}")


def post(url, payload, headers, timeout):
    request = Request(url, data=json.dumps(payload).encode(), headers={
        'Content-Type': 'application/json', **headers}, method='POST')
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as error:
        # Do not persist provider bodies/URLs that can echo credentials.
        raise ProviderHTTPError(error.code) from None


def endpoint(config):
    value = os.environ.get(config.get('base_url_env', ''), config.get('base_url', ''))
    parsed = urlparse(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('base_url must be http(s), without credentials or query parameters')
    if parsed.scheme == 'http' and parsed.hostname not in {'localhost', '127.0.0.1', '::1'} and not config.get('allow_private_http', False):
        raise ValueError('remote HTTP requires explicit allow_private_http for a trusted private network')
    return value.rstrip('/')


class Provider:
    def __init__(self, config, transport=post):
        self.c = config
        self.post = transport
        self.base = endpoint(config)
        self.kind = config['provider']
        self.model = config['model']
        self.timeout = config.get('timeout_seconds', 180)
        env = config.get('api_key_env')
        key = os.environ.get(env, '') if env else ''
        if env and not key:
            raise ValueError(f'missing environment variable: {env}')
        self.headers = ({'x-api-key': key, 'anthropic-version': '2023-06-01'} if self.kind == 'anthropic'
                        else {'x-goog-api-key': key} if self.kind == 'gemini'
                        else {'Authorization': f'Bearer {key}'} if key else {})

    def payload(self, request):
        messages = request['messages']
        settings = self.c.get('generation', {})
        if self.kind == 'anthropic':
            return dict(model=self.model, system='\n'.join(m['content'] for m in messages if m['role'] == 'system'),
                        messages=[m for m in messages if m['role'] != 'system'],
                        max_tokens=request['max_output_tokens'], **settings)
        if self.kind == 'gemini':
            return {'systemInstruction': {'parts': [{'text': m['content']} for m in messages if m['role'] == 'system']},
                    'contents': [{'role': 'user' if m['role'] == 'user' else 'model', 'parts': [{'text': m['content']}]}
                                 for m in messages if m['role'] != 'system'],
                    'generationConfig': {'maxOutputTokens': request['max_output_tokens'], **settings}}
        return dict(model=self.model, messages=messages, max_tokens=request['max_output_tokens'], **settings)

    def count(self, request):
        payload = self.payload(request)
        if self.kind == 'anthropic':
            payload.pop('max_tokens')
            # Count API accepts thinking but not sampling parameters.
            payload = {k: v for k, v in payload.items() if k in {'model', 'messages', 'system', 'thinking'}}
            data = self.post(self.base + '/messages/count_tokens', payload, self.headers, self.timeout)
            n = data['input_tokens']
        elif self.kind == 'gemini':
            data = self.post(self.base + '/models/' + quote(self.model, safe='') + ':countTokens',
                             {'generateContentRequest': {'model': 'models/' + self.model, **payload}}, self.headers, self.timeout)
            n = data['totalTokens']
        else:
            # vLLM's native /tokenize applies its actual served chat template.
            payload = {'model': self.model, 'messages': request['messages'], 'add_generation_prompt': True,
                       **self.c.get('tokenize_options', {})}
            url = self.c.get('tokenize_url') or self.base.removesuffix('/v1') + '/tokenize'
            data = self.post(url, payload, self.headers, self.timeout)
            n = data['count']
        if type(n) is not int or n < 1:
            raise ValueError('invalid provider token count')
        return n

    def generate(self, request):
        start = time.monotonic()
        path = ('/messages' if self.kind == 'anthropic' else
                '/models/' + quote(self.model, safe='') + ':generateContent' if self.kind == 'gemini' else '/chat/completions')
        raw = self.post(self.base + path, self.payload(request), self.headers, self.timeout)
        text, finish, usage = normalize(self.kind, raw)
        usage['latency_seconds'] = time.monotonic() - start
        return {'status': 'ok' if finish == 'stop' else 'failed', 'finish_reason': finish,
                'text': text, 'usage': usage, 'raw': raw}


def normalize(provider, raw):
    if provider == 'anthropic':
        blocks = raw.get('content', [])
        text = ''.join(b.get('text', '') for b in blocks if b.get('type') == 'text')
        reason = raw.get('stop_reason', 'missing_finish_reason')
        usage = raw.get('usage', {})
        normalized = {}
        if 'input_tokens' in usage and 'output_tokens' in usage:
            normalized = {'input_tokens': sum(usage.get(k, 0) for k in ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')),
                          'output_tokens': usage['output_tokens']}
        return text, 'stop' if reason == 'end_turn' else reason, normalized
    if provider == 'gemini':
        choices = raw.get('candidates', [])
        choice = choices[0] if len(choices) == 1 else {}
        text = ''.join(p.get('text', '') for p in choice.get('content', {}).get('parts', []) if not p.get('thought', False))
        reason = choice.get('finishReason', 'blocked_or_missing_candidate')
        usage = raw.get('usageMetadata', {})
        normalized = {}
        if 'promptTokenCount' in usage and 'candidatesTokenCount' in usage:
            normalized = {'input_tokens': usage['promptTokenCount'],
                          'output_tokens': usage['candidatesTokenCount'] + usage.get('thoughtsTokenCount', 0),
                          'reasoning_tokens': usage.get('thoughtsTokenCount', 0)}
        return text, 'stop' if reason == 'STOP' else reason, normalized
    choices = raw.get('choices', [])
    choice = choices[0] if len(choices) == 1 else {}
    message = choice.get('message', {})
    text = message.get('content') or ''
    reason = 'refusal' if message.get('refusal') else choice.get('finish_reason', 'missing_finish_reason')
    usage = raw.get('usage', {})
    normalized = {}
    if 'prompt_tokens' in usage and 'completion_tokens' in usage:
        normalized = {'input_tokens': usage['prompt_tokens'], 'output_tokens': usage['completion_tokens'],
                      'reasoning_tokens': usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)}
    return text, reason, normalized
