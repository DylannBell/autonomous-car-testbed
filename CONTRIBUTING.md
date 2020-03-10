# GitHub Usage Conventions

## Issues

For any work you are doing, you should create an issue in GitHub for it. Give it a relevant title and corresponding comment such that anyone in our team can understand it with minimal context.  

You should assign someone to work on an issue, either yourself or someone else. There can be multiple people working on a single issue.

If you see a bug or feature that needs to be addressed now or in the future, you should always add an issue, even if you can't work on it right now or if it's not your issue.

An issue will also have one branch (in most cases) assigned to it. When the Pull Request of this branch is approved and merged into master - the issues will be closed.

## Branches

For any work you are doing, you should create a branch and name it accordingly. It should also correspond to an issue.

All branches should have a token:

```
feat      Feature you are adding or expanding
bug       Bug fix or experiment
test      Branch for testing/verification
junk      Throwaway branch created to experiment
wip       Work in progress
```  

For example a new feature being added called "Search By Mac Address" could be something like:
```
feat/search_by_mac
```
Snake case should be used for branch names.

All commits should be made on the branch and then merged into the master branch using a pull request when work is complete.

## Pull Requests

When work is completed on a branch, a pull request should be used to merge it into master. At lease one reviewer should be added so that the code is looked over by someone else. 

When you have submitted the pull request, add the corresponding pull request to the issue so that when the pull request is approved, the issue will be closed as well.

## Commit Messages

Commit messages and body should be based off this guide:
```https://chris.beams.io/posts/git-commit/```


- Separate subject from body with a blank line
- Limit the subject line to 50 characters
- Capitalize the subject line
- Do not end the subject line with a period
- Use the imperative mood in the subject line
- Wrap the body at 72 characters
- Use the body to explain what and why vs. how

For example if you are updating the readme to include setup instructions:
``` 
Add setup instructions to readme
```