TABLE = '''<table>
	<thead>
		<tr>
			{% for header in headers %}
				<th>{{ header }}</th>
			{% endfor %}
		</tr>
	</thead>

	<tbody>
		{% for item in qs %}
			<tr>
				{% for field in item %}
					<td>{{ field }}</td>
				{% endfor %}
			</tr>
		{% endfor %}
	</tbody>
</table>'''

DL = '''<dl>
	{% for item in qs %}
		<dt>{{ item.0 }}</dt>
		<dd>{{ item.1 }}</dd>
	{% endfor %}
</dl>'''