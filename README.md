SQL Query Builder
---

This modules defines a class which allow the building of SQL queries in a functional style.

This class lazily builds SQL queries. Each method called on the class returns another `Query` object which will only get evaluated once the `build` method is called.

Example:
```python
q = Query('Person').select('id', 'age')
filtered = q.filter(name='Bill')
name_ordered = (filtered
    .select('name')
    .order_by('name')
    .build()
)
age_ordered = filtered.order_by('age').build()

name_ordered == 'SELECT id, age, name FROM Person where name='Bill' ORDER BY name;'

age_ordered == 'SELECT id, age FROM Person where name='Bill' ORDER BY age;'
```
