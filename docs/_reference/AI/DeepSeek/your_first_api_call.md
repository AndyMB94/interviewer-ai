# Quick Start

## Your First API Call

The DeepSeek API uses an API format compatible with OpenAI/Anthropic. By modifying the configuration, you can use the OpenAI/Anthropic SDK or softwares compatible with the OpenAI/Anthropic API to access the DeepSeek API.

| PARAM | VALUE |
| --- | --- |
| base_url (OpenAI) | https://api.deepseek.com |
| base_url (Anthropic) | https://api.deepseek.com/anthropic |
| api_key | apply for an API key |
| model | deepseek-v4-flash, deepseek-v4-pro |

### Integrate with Agent Tools

The DeepSeek API is supported by many popular AI agent and coding assistant tools. If you use tools like Claude Code, GitHub Copilot, or OpenCode, you can use DeepSeek as the backend model directly no code required.

See the Agent Integrations Guide for details.

### Invoke The Chat API

Once you have obtained an API key, you can access the DeepSeek model using the following example scripts in the OpenAI API format. This is a non-stream example, you can set the stream parameter to true to get stream response.

For examples using the Anthropic API format, please refer to Anthropic API.

`python`

```python
# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
)

print(response.choices[0].message.content)
```