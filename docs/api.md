# REST API Documentation

## General Conventions

All request and response data is passed and returned as JSON.

Successful responses contain a `data` field containing an object or list of
objects, depending on the request. Unsuccessful requests will have return with
an applicable HTTP status and an `error` field which has the following shape:
```
{
    'code': 'machine_readable_error_name',
    'description': 'More in-depth, human-readable error message',
}
```

Most requests also have a `links` field containing URLs to related resources.


## Types

Besides primitive types, some schemas for other objects are defined here for use
in the rest of the documentation. A question mark (`?`) after a type indicates
that the field is nullable / optional.

```
URL = string
```

Dates and times are in ISO 8601 format and stored in UTC.
```
Time = string
DateTime = string
```

```
User {
    id: int,
}
```

```
Question {
    id: int,
    // null indicates that the correct answer is unknown / is subjective
    correct_answer: bool?,
    more_info_link: string?,
    created_at: DateTime,
    expires_at: DateTime?,
}
```

```
Response {
    user_id: int,
    question_id: int,
    response: bool?, // null indicates that the question was skipped
    view_time: Time?,
    answered_at: DateTime,
}
```


## Users

User IDs can either be integral IDs returned by other methods in this API or the
string `"me"` to indicate the current signed-in user (if any).

Because most user data is stored and managed by the Azure Active Directory,
database entries for this application are created automatically whenever a
signed-in user makes a request for a resource which requires the created of said
entry. For example, responding to a question or requesting their own details.
Users can still be created explicitly, however, if the Azure subject identifier
(`sub`) is known.

### User Details

```
GET /users/<id> -> {
    data: User,
    links: {
        self: URL,
        responses: URL,
    },
}
```

### User List

```
GET /users -> {
    data: [User],
    links: {
        self: URL,
    },
}
```

### User Creation

```
POST /users {
    subject_identifier: string,
} -> {
    data: User,
    links: {
        self: URL,
        responses: URL,
    },
}
```


## Questions

### Question Details

```
GET /questions/<id> -> {
    data: Question,
    links: {
        self: URL,
    },
}
```

### Question List

```
GET /questions -> {
    data: [Question],
    links: {
        self: URL,
    },
}
```

### Question Creation

```
POST /questions {
    prompt: string,
    correct_answer: bool?,
    more_info_link: URL?,
    created_at: DateTime?, // Defaults to current time
    expires_at: DateTime?,
} -> {
    data: Question,
    links: {
        self: URL,
    },
}
```


### Question Modification

```
PUT /questions/<id> {
    prompt: string?,
    correct_answer: bool?,
    more_info_link: URL?,
    created_at: DateTime?,
    expires_at: DateTime?,
} -> {
    data: Question,
    links: {
        self: URL,
    },
}
```


## Responses

### Response Details

```
GET /users/<user_id>/responses/<question_id> -> {
    data: Response,
    links: {
        self: URL,
        user: URL, // User Details
        question: URL, // Question Details
    },
}
```

Note: This is also accessible via
`/questions/<question_id>/responses/<user_id>`, however the first endpoint is
the recommended / canonical one and is what will be returned by other endpoints.

### Response Creation and Modification

```
PUT /users/<user_id>/responses/<question_id> {
    response: bool?, // Required if the no response exists already
    view_time: Time?,
} -> {
    data: Response,
    links: {
        self: URL,
        user: URL, // User Details
        question: URL, // Question Details
    }
}
```

### User Response List

Responses made by a user; includes skipped questions.

```
GET /users/<user_id>/responses -> {
    data: [Response],
    links: {
        self: URL,
        user: URL, // User Details,
    },
}
```

### Question Response List

Responses made by all users for a question; includes users who skipped the
question.

```
GET /questions/<question_id>/responses -> {
    data: [Response],
    links: {
        self: URL,
        question: URL, // Question Details,
    },
}
```
