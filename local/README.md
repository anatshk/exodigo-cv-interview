# local/

Gitignored working inputs the code may need but git should not hold: sample inputs,
constraints, scratch data, model weights, exports. Readable by tooling and by Claude, but
never committed (only this README is tracked, so a fresh clone still gets the folder).

Anything that grants access (API keys, credentials, tokens, cookies, live session state)
does **not** belong here. That goes in `.secrets/`.
