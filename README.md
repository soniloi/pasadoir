# Pasadóir

Pasadóir is an IRC bot that generates text using individualized Markov chains based on given source material. It can be used to generate "new" phrases from a user based on things they have said before. It is written in python, using the Twisted framework.

## Terminology

The term "lookback tuple" refers to current state in the Markov chain. The length of the lookback tuple determines the quality of quote generated. In general, a lower tuple length will lead to longer, more rambling, and less coherent phrases. Conversely, a higher length will generate shorter, less varied, and more syntactically correct quotes, which are more likely to be exact matches to underlying source material. The tuple length is configurable for Pasadóir, and is set to 2 by default.

The term "transition table" is used here to describe how lookback tuples are mapped to potential following tokens.

## Example

Take a user with the following input set:
```
she sells sea-shells by the sea-shore
the dog was eating sausages by the dozen
```

The following are the possible outputs, where the lookback tuple length is 2:
```
she sells sea-shells by the sea-shore
she sells sea-shells by the dozen
the dog was eating sausages by the dozen
the dog was eating sausages by the sea-shore
```

# Pre-requisites

There must be a single input directory, containing the items listed below. The location of this directory does not matter; the directory name will be passed at run-time.

## Source material files

These are plain text files, each with the extension `.src`. The filename minus the extension is the username. The following format must apply.
* Each line of input is to be on its own line in the file.
* Each line is to have at least the same number of words as the lookback tuple length.

How the source material is generated is up to you. Typically, it will involve parsing IRC log files, stripping out very short lines, and maybe some normalization.

Note that the more input (both number of lines and number of words per line) we have for a user, the better the output will be. The generator works best when there are many possible successors to each tuple of words; the more possible successors, the more varied the generated lines.

### Sample source material file

Say we have a user with username `kitten`. In our sources directory there must be a file named `kitten.src`. Its contents could be something like this:

```
I yawn in your general direction
my occupation is mousing
om nom nom tasty fish
I'm just going to snooze here while I wait for my opportunity to pounce
```

## Metadata

An optional file called `source.info` may be added to the input directory. If present, this would contain metadata about source generation. The following attributes are supported.
* `date`: Unix timestamp of when the source material was generated.
* `channels`: Names of IRC channels used to generate the source material.

### Sample metadata file

```
date=1489964352
channels=#underthetree #kitten_test #sleep
```

## User merge information

An optional file called `merge.lst` may be added to the input directory. If present, this would contain mappings of user aliases (other nicks a user has been known by) to canonical nicknames. The file should be laid out as follows.
* Each user must be on its own line.
* Lines consist of tab-separated nicks.
* The first nick is the canonical one; all other nicks are aliases.

### Sample merge information file

```
kitten\tkitten_\tkitten1
user1\tUserOne
```

# Dependencies

* Python 3: tested with Python 3.8.10, other versions of Python 3.x may also work
* python3.x-venv

# Setup

```
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Testing

To run unit tests, run the following from the checkout location.
```
export PYTHONPATH=$PWD/src:$PYTHONPATH
python -m unittest discover test
```

# Running

Run the following command from the checkout location.
```
python src/bot.py <host> <port> <channel> <src_dir>
```
Where
* `host` and `port` are the host and port to run on.
* `channel` is the IRC channel for the bot to run in.
* `src_dir` is the location of the directory containing the source material as described above.

By default, the bot will connect with the nick `pasadoir`. If this is taken, then it will fail. The nick may be configured to something else in `config.py`.


## Usage

The instructions below indicate what to type in IRC to prompt the bot. First, you must connect to IRC as usual and join the channel the bot is in.

### Triggers

There are several different triggers for the Pasadóir bot. The bot looks only at lines starting with those characters, and ignores all others. These are all configurable, with the following defaults.

* `!` `^` `~`: these are all used to generate quotes; the differences between them will be described below.
* `@`: this is used for non-quote related commands.

### Generating basic quotes

Quotes are generated by typing one of the quote-generating triggers followed by a nickname. To generate a quote based on a single user named `kitten`, type the following.

```
!kitten
```

A quote may be generated from the source of multiple users combined. There is a limit to the number of users a quote may be generated for; this is determined by the cache size (see the section on caching below).

The syntax for this is to separate nicks with a colon.

```
!kitten:daffodil:user1
```

The ordering does not matter. The configurations below (or any other possible combinations) would produce exactly the same results.

```
!kitten:user1:daffodil
!daffodil:user1:kitten
```

### Seed words

Optionally, quotes may be seeded, meaning it is possible to give some words for the quote to start from.

A few notes on this:
* Seed words must be space-separated.
* While nicks and special-feature triggers are case-insensitive, seed words are case-sensitive.
* Seed words will match from anywhere within a user's (or multiple users') material, i.e. not just on their starting tuples.
* The number of seed words given must be less than or equal to the lookback tuple length.
* If no matching tuples or partial tuples are found, the bot will not output anything.

The different quote triggers are used to vary the behaviour of the seeding. The following defaults apply.

* `^` indicates that the quote is to start with the words given.
* `~` indicates that the quote is to end with the words given.
* `!` is used to indicate that the words given may appear anywhere in the quote, i.e. the generation runs bidirectionally from the seed words.

As an example, imagine a user `kitten` with the following source material, and where the tuple length is 2:
```
I yawn in your general direction
```

The following will be the result of various interactions:
```
| Input                | Output                                    |
|----------------------|-------------------------------------------|
| ^kitten I            | [kitten] I yawn in your general direction |
| ^kitten I yawn       | [kitten] I yawn in your general direction |
| ^kitten your         | [kitten] your general direction           |
| ~kitten direction    | [kitten] I yawn in your general direction |
| ~kitten your general | [kitten] I yawn in your general           |
| !kitten I            | [kitten] I yawn in your general direction |
| !kitten direction    | [kitten] I yawn in your general direction |
| !kitten your         | [kitten] I yawn in your general direction |
| !kitten in your      | [kitten] I yawn in your general direction |
```

Note that either the starts-with trigger `^` or the ends-with trigger `~` may also be used without arguments to generate basic quotes as well; however, without seed words there is no specific reason to use them.

### Notes

* If the bot is called on a username that does not exist, then it does not do anything.
* If the bot is called on a nick that is an alias, then the real user will be resolved.
* If it is called for a combination of a user that exists and one that does not, then it will only return a quote for one that exists.

### Getting basic information

To see basic general numbers, run:
```
@stats
```

To see basic information relating to a specific user, run:
```
@stats <nick>
```

## Caching

At start time, a user list is constructed based on the source files found in the given source directory. However, as the source material itself may be quite large, it is not loaded at start time. Because building transition tables may be quite slow (especially for multi-user quotes) a cache is maintained containing tables for the most recently-called users (or combinations of users).

When a quote is requested for a user that is not already in the cache, that user's transition table is built and placed in the cache. The cache is keyed by user(s) and by directionality (keeping in mind that a different table must be built depending on whether the quote runs forwards or backwards from a seed).

The number of slots in the cache is configurable. If the cache is full and a quote is requested of a user not in the cache, then the least recently called user is evicted.

When generating a quote from multiple users' source, each of those users is read into the cache, as well as their combined transition table. For this reason, the number of users that may be combined is limited by the cache size.

If a quote is requested for a user already in the cache, then that user's transition table is returned directly. This speeds up access, but may also lead to stale information, e.g. where the content on disk has been updated. To purge the cache, run:
```
@refresh
```
