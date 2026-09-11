<p align="center">
  <img src="ask-apple/assets/ask-apple_circular.png" alt="Ask Apple" width="140">
</p>

<h1 align="center">Ask Apple Skill</h1>

<p align="center">
  <img alt="AI Agents - Skill" src="https://img.shields.io/badge/AI--Agents-Skill-EF9035?style=flat">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-blue?style=flat"></a>
  <a href="https://www.linkedin.com/in/wolfgang-muhsal-12408194/"><img alt="LinkedIn" src="https://img.shields.io/badge/Contact-LinkedIn-95a5a6.svg?style=flat"></a>
</p>

Ask Apple is an agent skill for Codex and other AI coding assistants that sends development questions to the AI-backed search on Apple Developer.

It requests Apple's generated answer, quick results, and mixed search results together, then reassembles the streamed response and provides direct links to the underlying Apple documentation, sample code, videos, and WWDC material. Focused searches for Documentation, Videos, Sample Code, or WWDC26 results are available on request.

## Why This Matters

Apple Developer Search combines source discovery with an AI-generated answer. Ask Apple makes that complete response available inside an agent workflow, so developers can ask a technical question and continue working with both the concise answer and the supporting Apple resources.

The skill keeps the three default result channels together. Category searches remain optional, so agents retrieve the broader Documentation, Videos, Sample Code, or WWDC26 result sets only when requested.

## Installing Ask Apple

Install the skill with `npx`:

```bash
npx skills add https://github.com/Gucky/AskApple --skill ask-apple
```

To install it globally for Codex:

```bash
npx skills add https://github.com/Gucky/AskApple --skill ask-apple --agent codex --global
```

For a specific agent:

```bash
npx skills add https://github.com/Gucky/AskApple --skill ask-apple --agent claude-code
```

For all supported agents:

```bash
npx skills add https://github.com/Gucky/AskApple --skill ask-apple --agent '*'
```

## Using Ask Apple

In Codex, trigger the skill directly:

```text
$ask-apple How should I adopt Swift concurrency in this type?
```

You can also ask naturally:

```text
Use the Ask Apple skill to ask how Transferable works.
```

Ask for a focused follow-up only when you need it:

```text
Now search specifically for Apple Developer videos about this question.
```

The skill helps agents to:

- retrieve Apple's AI-generated answer and its cited sources;
- collect quick search results when Apple provides them;
- collect the mixed results from Apple's **All** search;
- follow up with focused Documentation, Videos, Sample Code, or WWDC26 searches when requested; and
- provide direct Apple links for verification and further reading.

## Scope and Safety

The skill sends the supplied question to Apple. It does not add repository contents, local files, credentials, personal data, or unrelated agent context to the request.

Apple labels generated answers as AI-generated information that should be verified against the linked source material.

## Requirements

- Python 3 using only the standard library
- Outbound HTTPS access to Apple Developer Search
- Node.js for `npx` installation
- An AI coding assistant that supports agent skills

## License

Ask Apple was created by [Wolfgang Muhsal](https://github.com/Gucky). It is available under the [MIT License](LICENSE).
