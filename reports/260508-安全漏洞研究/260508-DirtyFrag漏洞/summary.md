# Dirty Frag vulnerability research note

Source analyzed:
- https://www.openwall.com/lists/oss-security/2026/05/07/8
- https://github.com/V4bel/dirtyfrag
- https://raw.githubusercontent.com/V4bel/dirtyfrag/master/assets/write-up.md

Summary:
- Dirty Frag is reported as a Linux local privilege escalation vulnerability chain.
- It chains two kernel page-cache write issues: xfrm-ESP Page-Cache Write and RxRPC Page-Cache Write.
- Both issues involve zero-copy/splice paths placing read-only file page-cache pages into skb fragments, then receiver-side in-place crypto writes back into those fragments.
- Practical impact: an unprivileged local user may obtain root on major Linux distributions if the relevant kernel modules/features are available.
- The original disclosure states that public release happened after an embargo break, so distribution fixes/CVEs may lag the publication.

Defensive guidance:
- Apply vendor kernel updates as soon as distributions publish backports.
- Until patched, block relevant modules: esp4, esp6, rxrpc.
- Review whether unprivileged user namespaces are enabled; disabling them can reduce exposure for the ESP path but is not a complete mitigation for the RxRPC path.
- Treat multi-user Linux hosts, CI runners, developer workstations, container hosts, and shared GPU/compute servers as high priority.
- Reboot after kernel updates or module changes where required, and verify module state after boot.

Temporary mitigation from the advisory:

```sh
sh -c "printf 'install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n' > /etc/modprobe.d/dirtyfrag.conf; rmmod esp4 esp6 rxrpc 2>/dev/null; true"
```
