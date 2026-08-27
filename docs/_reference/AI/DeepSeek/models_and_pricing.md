# Quick Start

## Models & Pricing

The prices listed below are in units of per 1M tokens. A token, the smallest unit of text that the model recognizes, can be a word, a number, or even a punctuation mark. We will bill based on the total number of input and output tokens by the model.

### Model Details

| MODEL | deepseek-v4-pro | deepseek-v4-flash |
| --- | --- | --- |
| **BASE URL (OpenAI Format)** | https://api.deepseek.com | https://api.deepseek.com |
| **BASE URL (Anthropic Format)** | https://api.deepseek.com/anthropic | https://api.deepseek.com/anthropic |
| **MODEL VERSION** | DeepSeek-V4-Pro | DeepSeek-V4-Flash |
| **THINKING MODE** | Supports both non-thinking and thinking (default) modes. See Thinking Mode for how to switch | Supports both non-thinking and thinking (default) modes. See Thinking Mode for how to switch |
| **CONTEXT LENGTH** | 1M | 1M |
| **MAX OUTPUT** | MAXIMUM: 384K | MAXIMUM: 384K |
| **Json Output** | ✓ | ✓ |
| **Tool Calls** | ✓ | ✓ |
| **Chat Prefix Completion (Beta)** | ✓ | ✓ |
| **FIM Completion (Beta)** | Non-thinking mode only | Non-thinking mode only |
| **1M INPUT TOKENS (CACHE HIT)** | $0.003625 | $0.0028 |
| **1M INPUT TOKENS (CACHE MISS)** | $0.435 | $0.14 |
| **1M OUTPUT TOKENS** | $0.87 | $0.28 |
| **Concurrency Limit(1)** | 500 | 2500 |

*(1) For more details on concurrency limits, please refer to Rate Limit & Isolation*

### Deduction Rules

The expense = number of tokens x price. The corresponding fees will be directly deducted from your topped-up balance or granted balance, with a preference for using the granted balance first when both balances are available.

Product prices may vary and DeepSeek reserves the right to adjust them. We recommend topping up based on your actual usage and regularly checking this page for the most recent pricing information.