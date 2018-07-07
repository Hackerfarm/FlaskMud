<hr>
With great power comes great fun!

<h2>Create place</h2>
<form name='create_place' action='/admin/create_place' method='POST'>
Short name: <input type=text name='name'/>
<input type=submit value='create place'/>
</form>

<h2>Create path</h2>
<form name='create_path' action='/admin/create_path' method='POST'>
From: <select name="src">
{% for p in places %}
	<option value="{{p[0]}}">{{p[1]}}</option>
{% endfor %}
</select> to: <select name="dst">
{% for p in places %}
	<option value="{{p[0]}}">{{p[1]}}</option>
{% endfor %}
</select>
description:<input type=text name=desc>
<input type=submit value='create path'/>
</form>

<h2>Create object</h2>
<form name='create_object' action='/admin/create_object' method='POST'>
Short description: <input type=text name=desc>
Location: <select name=location>
{% for p in places %}
	<option value="{{p[0]}}">{{p[1]}}</option>
{% endfor %}
</select>
<input type=submit value='create object'/>
</form>

<h2>Teleport people</h2>
<form name='teleport_people' action='/admin/teleport_people' method='POST'>
Character:
<select name=person>
{% for p in characters %}
	<option value="{{p[0]}}">{{p[1]}}</option>
{% endfor %}
</select>
Location:
<select name=location>
{% for p in places %}
	<option value="{{p[0]}}">{{p[1]}}</option>
{% endfor %}
</select>
<input type=submit value='teleport'/>
</form>
