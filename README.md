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

## Random ideas

 - Evaluate a possibility to inter-operate with Git, reuse Git for distributed
   workflows, or even complex local workflows. Evaluate a possibility to use
   FVCS *within* a Git repository.
