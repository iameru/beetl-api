# beetl-api

the api to handle the beetl stuff.

All data is in theory fetchable by everyone. There are no user accounts.

However, every beetl gets a random `obfuscation` part in its url.
After `POST`ing a beetl or a bid you get a randomly generated `secretkey` in
the response which is needed to edit your bid or beetl again.

This should be secure enough for many usecases, especially under the assumption
that this app does not handle any critical data.


## openapi docs url

docs_url="/api/docs"
redoc_url="/api/redoc"
