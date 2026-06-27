# Omnibox

`omnibox.py` is a compact, standard-library-only Python CLI that combines four high-leverage utilities:

- `grep`: recursively regex-search files, directories, or standard input.
- `json`: read JSON from standard input and select a dotted path, including list indexes.
- `hash`: calculate file, directory, or standard-input digests with any available `hashlib` algorithm.
- `serve`: expose a directory through a tiny local HTTP server.

## Examples

```bash
python omnibox.py grep TODO src -i
printf '{"users":[{"name":"Ada"}]}' | python omnibox.py json users.0.name
python omnibox.py hash README.md -a sha256
python omnibox.py serve . -p 8000
```
