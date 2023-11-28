# FVCS

An experimental file-centric version control system (every file has its own
version history).

## Goals. Expected features.

Goals:

 - evaluate the usability of a file-centric version control in modern software
   development environment
 - have fun reimplementing what SCSS did several decades ago

Expected features:

 - **file-centric**: every file has its own version history (as opposed to
   repository-based VCS: Git, Mercurial, or Subversion, for instance)
 - **local data model**: local repository is self-contained, including all data
   and history
 - ~~**distributed data model**: to be built on top of a local data model, can
   be added later on~~
 - **minimalistic** and **ejectable**: based on existing tools (e.g., `diff`),
   data and history can be accessed, extracted and even modified (corrected)
   directly in the file system using commonly-available command-line tools

Status: in progress, experimental, some features may be not available

## Advantages and disadvantages of file-centric version control

**Advantages**:

 - Isolation and independence: changes to one file do not affect the versioning
   or history of other files; allows to work on different files without
   interference.
 - Fine-grained version control: useful when different files in a project have
   different lifecycles or when you want to manage changes to specific files
   separately.
 - Simplicity: file-centric model is easier to understand.
 - Flexibility: theoretically, repository-centric versioning is a superset of a
   file-centric versioning; latter ultimately should allow more flexible usage
   workflows

**Disadvantages**:

The objective of this project is to overcome many of the disadvantages that are
inherent to the file-centric model. Most of the disadvantages are related to
the difficulty to manage the following scenarios:

 - Complex development workflows (branching, merging, etc.)
 - Distributed and collaborative workflows
 - Handling the entire source tree as a cohesive unit

**Suitability**:

File-centric VCS is expected to be most suitable for projects where high degree
of isolation between distinct files is necessary, or already exists. For
example: version control of a set of distinct scripts, version control of user
dotfiles, etc.

## Design

This implementation being experimental, it is important to be able to:

 - avoid irrecoverable data and history corruptions
 - extract data and history in all situations
   - ideally, even eject into a traditional VCS: Git, for example
 - confidently fix errors directly in the internal data model

For these reasons, the design choices are minimalist and based on reusability
of existing and well-known tools (e.g., use `diff` and `patch` instead of
implementing own diff algorithms).

## Usage

    # initialize a repository
    fv init

    # add a file
    echo "Hello, World!\n" > README.txt
    fv add README.txt --comment "Created the README"

    # modify a file
    echo "Hello, FVCS!\n" >> README.txt
    fv diff README.txt
    fv update README.txt -c "Updated the README"

    # add another file, modify it several times
    echo "foo\n" > foo.txt
    fv add foo.txt -c "foo"
    echo "bar\n" >> foo.txt
    fv update foo.txt -c "bar"
    echo "baz\n" >> foo.txt
    fv update foo.txt -c "baz"

    # snapshot across all files in a repository:
    fv snapshot SNAPSHOT_NAME -c "First snapshot"

    # update several files at once (each change is recorded separately)
    echo "Hello, fine-grained version control" >> README.txt
    echo "qux" >> foo.txt
    fv update *.txt -c "Updated all text files"

    # show single files history:
    fv hist README.txt
    fv hist foo.txt

    # get a specific file version
    fv get README.txt --version 1
    fv get README.txt --snapshot SNAPSHOT_NAME

    # restore an entire repository to a snapshot
    fv restore SNAPSHOT_NAME

    # create a file version that removes it
    fv rm README.txt -c "Delete the README"  # doesn't delete its history

    # remove the file and its history (forget it)
    fv purge README.txt  # deletes the file and its history

    # eject, use snapshots as repository versions (implies current latest too)
    fv eject --snapshots
    # eject, interpret every change as a repository version
    # (uses update timestamps to order the changes)
    fv eject --file-versions

## Data and history storage format

All data and history is stored in a ".fvcs" directory in the root of a
repository:

 - `.fvcs/tree`: files and diffs (history)
   Every file in the repository has an according direcotory under `.fvcs/tree`
   with the same relative path; this directory stores all diffs of a file. Any
   file version can be restored by rolling up all diffs (patching) up to a
   target version.
 - `.fvcs/snapshots`: snapshot data
   Every snapshot is a TOML file with references to repository files and their
   versions. Files that didn't exist in the repository by the time the snapshot
   was created are naturally not listed.

## Random ideas

 - Evaluate a possibility to inter-operate with Git, reuse Git for distributed
   workflows, or even complex local workflows. Evaluate a possibility to use
   FVCS *within* a Git repository.
