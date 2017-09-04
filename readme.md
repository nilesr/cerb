## erb but for c

For use with [kore](https://kore.io)

Make a views directory outside your source directory, and put `example.cerb` in it. Then run cerb, and use it like this

```c
	#include <views.h>
	// ...
	char* result = cerb_example(NULL);
	http_response(req, 200, result, strlen(result));
	return (KORE_RESULT_OK);
```

In the future, you'll be able to pass variables in to the function

Also you'll have to rerun cerb every time you change your view
