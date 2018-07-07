<html>
<title>Flask RPG</title>
<body>
<p>Welcome {{username}},<br>
{{characname}} is now at {{location}} and has access to:<br>
<ul>
{% for l in access %}
	<li><A HREF="/go/{{l[1]}}">{{l[0]}}</A> through {{l[2]}}</li>
{% endfor %}
</ul>
</p>

{% if people|length>0 %}
    People in this place:
    <ul>
    {% for l in people %}
        <li>{{l['name']}}</li>
    {% endfor %}
    </ul>
{% endif %}

{% if objects|length>0 %}
    Objects in this place:
    <ul>
    {% for l in objects %}
        <li>{{l['desc']}}</li>
    {% endfor %}
    </ul>
{% endif %}

<a href='http://log:out@localhost:8088/logout'>logout</a>
</body>

</html>
