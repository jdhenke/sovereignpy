# Sovereign Server In Python

See the [original sovereign](https://github.com/jdhenke/sovereign) repo for full context.

This is that, but in python.

## Usage

Here's how to run the server and an example client that submits a patch to reject all future patches then tries to revert that patch but can't.

### Server

In a terminal, run:

```bash
git clone git@github.com:jdhenke/sovereignpy.git server
cd server
python3 main.py
```

The sever is now running and should log something like this:

```
Starting server...
```

### Client

In a separate terminal, create a client directory like this:

```bash
git clone server/.git client
cd client
```

Next, make this change to reject all future patches. The diff should look like this, which, if copied, can be applied with `pbpaste | git apply` on a Mac:

```diff
diff --git a/main.py b/main.py
index 7d2e4fb..82be561 100644
--- a/main.py
+++ b/main.py
@@ -39,7 +39,7 @@ class Server(BaseHTTPRequestHandler):
 
     # raises an exception if the patch should not be applied
     def verify(self, patch):
-        pass # always accept
+        raise Exception("rejected") # always reject
 
     # applies the patch to the source code in this directory
     def apply(self, patch):

```

Now commit and submit this patch to the server:

```
git add main.py
git commit -m 'Reject all patches'
git format-patch --stdout origin/master| curl -XPOST --data-binary @- localhost:8080
```

The server should respond with:

```
OK
```

And the server logs should look like this:

```
Applying: Reject all patches
127.0.0.1 - - [10/Feb/2022 20:40:53] "POST / HTTP/1.1" 200 -
Restarting server...
Starting server...
```

Now try and revert this patch:

```
git pull -r
git revert HEAD --no-edit
git format-patch --stdout origin/master| curl -XPOST --data-binary @- localhost:8080
```

The server should now respond with:

```
rejected
```

And the server logs should show this as a 400:

```
127.0.0.1 - - [10/Feb/2022 20:41:19] "POST / HTTP/1.1" 400 -
```

To see the current code the server is running, use a `GET` request. `grep`ing for the verify function specifically can be done like this:

```
curl -s localhost:8080 | grep -C1 'def verify'
```

This should show the line of code you just changed above and is the reason why your last submission was just rejected:

```python
    # raises an exception if the patch should not be applied
    def verify(self, patch):
        raise Exception("rejected") # always reject
```

Congrats. You broke it.

To see why this can actually be interesting, see the original [sovereign repo](https://github.com/jdhenke/sovereign).
