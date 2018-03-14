# Utility for get url/ip if DNS server not working.

# Usage

```bash
$ try2connect --url "http://example.com"
$ "http://example.com"
```

If not working DNS and at least once resolved domain `example.com`

```bash
$ try2connect --url "http://example.com"
$ "http://1.2.3.4"

```

# Install