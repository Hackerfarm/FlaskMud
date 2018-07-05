<hr>

With great power comes great fun!

<form name='create_place' action='/admin/create_place' method='POST'>
Nom court: <input type=text name='name'/>
<input type=submit value='créer le lieu'/>
</form>
<br>
<form name='create_path' action='/admin/create_path' method='POST'>
Depuis: <select name="src">
%for p in places:
	<option value="{{p[0]}}">{{p[1]}}</option>
%end
</select> vers: <select name="dst">
% for p in places:
	<option value="{{p[0]}}">{{p[1]}}</option>
%end
</select>
<input type=text name=desc>
<input type=submit value='créer le lien'/>
</form>
