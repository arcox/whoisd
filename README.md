# whoisd
A WHOIS daemon inspired by the authors of http://dan.drydog.com/swhoisd/

- Written in Python 3
- Simple configuration in the server.conf JSON file
- The data.json file is read only during startup.  Must restart the daemon to pickup changes.
- Entry fields starting with the "!" character indicate searchable data.  All such "exclaimed" fields that match the query will return the entire record in the results.

For example, when using the provided example JSON:
```
QUERY:  com
RESULT:
*** FOUND THE FOLLOWING INFORMATION ***

-- Record 1 of 3 --
domain: red.com
admin: Rojo Cardinal
ip: 11.22.33.44
nameserver1: birds.com
nameserver2: rainbow.org

-- Record 2 of 3 --
domain: green.net
admin: Verde Condor
ip: 5.6.7.8
nameserver1: birds.com
nameserver2: rainbow.org

-- Record 3 of 3 --
domain: blue.com
admin: Azul Eagle
ip: 123.123.123.1
nameserver1: colors.com
nameserver2: rainbow.org

*** END TRANSMISSION ***

QUERY:  birds
RESULT:
*** FOUND THE FOLLOWING INFORMATION ***

-- Record 1 of 1 --
domain: green.net
admin: Verde Condor
ip: 5.6.7.8
nameserver1: birds.com
nameserver2: rainbow.org

*** END TRANSMISSION ***
```
