<html>
<head>JDR 1</head>
<body>
<p>Bouh!</p>
<p>Bienvenue {{username}},<br>
{{characname}} se trouve en ce moment à {{location}}.<br>
Il a accès à:
<ul>
%for l in access:
	<li><A HREF="/go/{{l[1]}}">{{l[0]}}</A></li>
%end
</ul>
</p>

</body>

</html>
