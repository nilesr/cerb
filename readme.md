## erb but for c

For use with [kore](https://kore.io)

Make a views directory outside your source directory, and put `example.cerb` in it. Then run cerb, and use it like this

```c
	#include <views.h>
	// ...
	char* result = Cerb(example, {"test", "a"});
	http_response(req, 200, result, strlen(result));
	// do NOT free result here
	return KORE_RESULT_OK;
```

It should look something like this

![](ss.png)

You'll have to rerun cerb every time you change your view

If you don't want any locals, just pass `NULL` as the second argument to `Cerb`
