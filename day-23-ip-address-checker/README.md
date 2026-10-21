# Day 23 — IP Address Checker

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A small CLI that validates IPv4 and IPv6 addresses and CIDR networks, tells you what kind of address it is (public, private, loopback, link-local, multicast, carrier-grade NAT, documentation...), and shows handy forms like binary, integer and reverse-DNS pointer. For networks it prints netmask, broadcast, wildcard, host range and usable host count. Optional free geo lookup, no API key.

## Features

- Validates IPv4, IPv6 and CIDR ranges (`10.0.0.0/8`, `2001:db8::/32`)
- Address type detection, IPv4 class, IPv4-mapped IPv6 support
- Binary, integer, compressed/exploded and `in-addr.arpa` / `ip6.arpa` forms
- Subnet calculator: netmask, broadcast, wildcard, first/last host, usable hosts
- `--rdns` reverse DNS hostname lookup
- `--geo` city / country / ISP / ASN for public IPs and `--me` for your own public IP (free [ipapi.co](https://ipapi.co), no key)
- Text or `--json` output; args, `-f file`, piped stdin or interactive prompt
- Exit code `0` when everything is valid, `1` otherwise

## Run

```bash
cd day-23-ip-address-checker
python3 main.py --help
```

## Usage

```bash
python3 main.py 8.8.8.8                       # check one address
python3 main.py 192.168.1.0/24                # subnet details
python3 main.py 8.8.8.8 1.1.1.1 --geo         # add location / ISP
python3 main.py --me                          # your public IP
python3 main.py --rdns 8.8.8.8                # reverse DNS
python3 main.py -f ips.txt --json > report.json
cat ips.txt | python3 main.py
```

## Example

```text
$ python3 main.py 8.8.8.8 192.168.1.0/24 2001:db8::1 256.1.1.1
[VALID  ] 8.8.8.8  (IPv4 address, public)
          compressed       8.8.8.8
          exploded         8.8.8.8
          integer          134744072
          reverse_pointer  8.8.8.8.in-addr.arpa
          binary           00001000.00001000.00001000.00001000
          class            A
[VALID  ] 192.168.1.0/24  (IPv4 network, private)
          network          192.168.1.0
          prefix           24
          netmask          255.255.255.0
          addresses        256
          usable_hosts     254
          broadcast        192.168.1.255
          wildcard         0.0.0.255
          host_range       192.168.1.1 - 192.168.1.254
[VALID  ] 2001:db8::1  (IPv6 address, documentation (example-only))
          compressed       2001:db8::1
          exploded         2001:0db8:0000:0000:0000:0000:0000:0001
          integer          42540766411282592856903984951653826561
          reverse_pointer  1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa
[INVALID] 256.1.1.1
          x '256.1.1.1' does not appear to be an IPv4 or IPv6 address

3/4 valid
```

## Requirements

Python 3.8+. Standard library only. Internet is needed only for `--geo`, `--me` and `--rdns` (ipapi.co free tier is rate-limited).
