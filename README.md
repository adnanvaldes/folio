## Folio

For some years I have been tracking data on a SQLite database, often manually writing SQL statements to add or update the information contained in the file. After sometime I upgraded the interface to a tiny Python script that wrote data into the SQLite file, although I had to open the file to specify the table and row values anytime I wanted to make a change - the script consisted of about 3 lines of code.

The setup worked fine (in fact, it still does) because most of the values didn't change often. Book information was the most likely to change, and in any case I haven't been very good at keeping track of this (so far I use my bullet journal).

This project's *raison d'etre* is primarily to practice implementing software development patterns and architectures, based largely on the Gang of Four [design patterns](https://refactoring.guru/design-patterns) and the architectural principles described in [Architecture Patterns with Python](https://https://www.cosmicpython.com/). More generally, it is an attempt to:

1) apply SOLID principles
2) use GoF design patterns
3) practice architecture design
4) create a usable CLI app for myself

The expected result is an over-engineered but usable and extensible CLI app to do what I could do before with a simple script.

## On models

### Work and Book

The first two models are `Work` and `Book`. These two are related, in that a `Book` is a concrete version of a `Work`; the `Work`, on the other hand, is the product of a literary effort.

This distinction is used to connect multiple `Book`s (such as those in different formats or editions) to a single, unifying `Work`. The use-case for this is that I often have both digital and physical copies of a book (and sometimes audiobooks, too); however, when thinking about whether a book was been read or not we often refer to the _work_ - the specific instance of that _work_ is less important in conversation (unless you are an academic, for example, and need bibliographic data).

Because of this, a `Work` is defined as a `title`, `author` with optional `year` and `genre` information. Editions of that `work` may be published at different times, but there is (usually) only a single year that an author finished a `work`. Likewise, a `work` encodes `is_read` as a boolean: in most cases, I would consider a book "read" regardless of which edition or format I read it it.

On the other hand, a `Book` is defined by a `Work`, page count, format, and ISBN. In theory it should be possible to simply use ISBN to specify the `book`, since those are distinct numbers assigned to each edition or a book. However, the domain model of this application allows for `None` (or `null`, I suppose) ISBN values, and compares books based on their `Work`, the `Format`, _and_ the ISBN. This is done primarily as a convenience - I often don't actually know what the ISBN is, or digital management applications, such as Calibre, often grab an ISBN for a different edition. Accurate ISBNs are far less important to me than the record of a `Work`. I could have simply defined a book as an object that contains a `Work` and a `Format`.

The presence of a `Book` indicates ownership of that edition; this is to manage books I have borrowed but do not own myself.

#### Work

| Title         | Author      | Year | Genre   | is_read |
| ------------- | ----------- | ---- | ------- | ------- |
| Hyperion      | Dan Simmons | 1989 | Scifi   | True    |
| The Histories | Herodotus   | -430 | History | True    |

Each row represents a literary `Work`, which contains :

- `title` of the work
- `author` (if multiple or unknown, then simply the colloquial use, since this is ultimately designed to be human-readable. Simply put, if I describe a work to someone, the author that I mention in conversation is the one that goes in this column).
- `year` the book was written. Negative numbers used for BCE dates
- `genre` as the *primary* genre when described to someone else. For instance, *Hyperion* is described as "SciFi, Fantasy, Space Opera", etc. These coalesce into "SciFi".
- `is_read` defines whether I have read the work

#### Book

| Work                      | Pages | Format | ISBN          |
| ------------------------- | ----- | ------ | ------------- |
| Hyperion - Dan Simmons    | 482   | Print  | 9780385249492 |
| The Histories - Herodotus | 784   | Ebook  | 9780140449082 |

Each row represents a `Book`, such that:

- `work` is the [work](#work) the book contains
- `pages` is the page number of this edition
- `format` is one of `"Audio", "Print", or "Ebook"
- `isbn` is the ISBN-13 of the edition


### Travel

I started tracking my travel a few years ago, when I was preparing a citizenship application. The requirement was to calculate the total time present in the country, and every exit delayed the process. As a result, I began to simply keep a record of _international_ travel in the following format:

| Origin | Destination | Date       | Notes                               |
| ------ | ----------- | ---------- | ----------------------------------- |
| CAN    | USA         | 1900-01-01 | Entered via Houston                 |
| USA    | MEX         | 1900-02-25 | Entered via Mexico City, vacation   |
| MEX    | CAN         | 1901-11-01 |                                     |

Each row represents a unit of travel across an international border where `date` is the date of _entry_ into a new country. While it is possible to keep track of _exit_ dates, that much granularity seems unnecessary for my purposes.

Country codes are written using  [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3), dates with [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), and notes are simply text fields.

### Addresses

There are a few - but often critical - situations where having a detailed history of addresses is necessary. Just like with [travel](#travel), government-related services can require this kind of detail (often to the previous 5-year period). Nonetheless, I find it useful to simply keep a record with basic fields, such as `start`, `end`, `address`, etc. 

| Start      | End        | Street Address          | Province      | Country | Postal Code | Notes |
| ---------- | ---------- | ----------------------- | ------------- | ------- | ----------- | ----- |
| 1900-01-1  | 1902-01-25 | Apt 1 - 123 Street Name | Province Name | CAN     | V0V V0V     |       |
| 1902-01-26 | 2025-01-01 | 456 Road Name           |               | MEX     | 10000       |       |
Each row represents a primary address, such that:

- `start` is the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) date I started living there
- `end` is the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) I left (or the current date if I still live there)
- `street address` is the street address of the place, including apartment number if required
- `province` is the sub-division of a nation into state, province, or what have you. Some countries don't use it, so it can be blank
- `country` is the [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country code
- `postal code` is the postal code of the location.

Due to variability in addresses between countries, most of these fields are simply text fields with no validation whatsoever.


### Employment

Much like [addresses](#addresses), I keep track of places I've worked. In the data I include relevant phone numbers, addresses, and employment periods. The `Employment` data includes the following fields:

| Start      | End        | Period | Company          | Supervisor | Address                                        | Phone number |
| ---------- | ---------- | ------ | ---------------- | ---------- | ---------------------------------------------- | ------------ |
| 1900-01-01 | 1902-01-01 | 1      | ABC Company      | Jane Smith | Unit 1 - 123 Street Name, Country, Postal Code | 123456789    |
| 1900-01-01 | 2025-01-01 | 124    | DEF Organization | John Doe   | 456 Address, Province, Country, Postal code    | 987654321    |
Each row represents a period of employment where:
- `start` is the [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) date when employment began
- `end` is the [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) date when employment ended (or the current date if still employed there)
- `period` is the difference between `start` and `end`
- `company` is the name of the organization
- `supervisor` is the last supervisor I had
- `address` is the address of the company
- `phone number` is the company official phone number. Does not include country codes.

Note that `address` here does not map to the [Addresses](#addresses) object. The former represents places I have lived and care to track, whereas `address` here is simply the official business address.


