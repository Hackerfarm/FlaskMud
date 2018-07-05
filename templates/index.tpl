<html>
<head>JDR 1</head>
<body>
<p>Bouh!</p>
<p>Welcome {{username}},<br>
{{characname}} is now at {{location}} and has access to:<br>
<ul>
%for l in access:
	<li><A HREF="/go/{{l[1]}}">{{l[0]}}</A> through {{l[2]}}</li>
%end
</ul>
</p>

</body>

</html>
