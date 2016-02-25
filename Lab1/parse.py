fh = open("access.log")

#Exercise: most visited URL? how to sort=

keywords = "Windows", "Linux", "Mac", "Ubuntu", "Googlebot", "YandexBot", "facebook", "Android"
d = {}
total = 0

for line in fh:
    total = total + 1
    try:
        timestamp, request, response, _, _, agent, _ = line.split("\"")
        method, path, protocol = request.split(" ")
        for keyword in keywords:
            if keyword in agent:
                d[keyword] = d.get(keyword, 0) + 1
                break #Stop researching for other keywords
    except ValueError:
        pass

interesting_total = sum(d.values())
print "Total lien with requested keywords:", sum(d.values())

for key, value in d.items():
    print key, "==>", value, "(", value * 100/ interesting_total, "%)"
    print "%s => %d (%.02f%%)" % (key, value, value * 100 / total)
