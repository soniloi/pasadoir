# Pasadóir

Pasadóir is an IRC bot that generates text using individualized Markov chains based on given source material. It can be used to generate "new" phrases from a user based on things they have said before. It is written in python, using the Twisted framework.

## Terminology

The term "lookback tuple" refers to current state in the Markov chain. The length of the lookback tuple determines the quality of quote generated. In general, a lower tuple length will lead to longer, more rambling, and less coherent phrases. Conversely, a higher length will generate shorter, less varied, and more syntactically correct quotes, which are more likely to be exact matches to underlying source material.

The tuple length is configurable for Pasadóir, and is set to 2 by default.

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
