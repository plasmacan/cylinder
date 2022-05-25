# https://github.com/markdownlint/markdownlint/blob/v0.9.0/docs/RULES.md

rule "MD001" # Header levels should only increment by one level at a time
rule "MD002", :level => 1 # First header should be a top level header
rule "MD003", :style => :atx # Header style
rule "MD004", :style => :asterisk # Unordered list style
rule "MD005" # Inconsistent indentation for list items at the same level
rule "MD006" # Consider starting bulleted lists at the beginning of the line
rule "MD007", :indent => 2 # Unordered list indentation
rule "MD009", :br_spaces => 0 # Trailing spaces
rule "MD010" # Hard tabs
rule "MD011" # Reversed link syntax
rule "MD012" # Multiple consecutive blank lines
rule "MD013", :line_length => 119, :code_blocks => true, :tables => true # Line length
rule "MD014" # Dollar signs used before commands without showing output
rule "MD018" # No space after hash on atx style header
rule "MD019" # Multiple spaces after hash on atx style header
rule "MD020" # No space inside hashes on closed atx style header
rule "MD021" # Multiple spaces inside hashes on closed atx style header
rule "MD022" # Headers should be surrounded by blank lines
rule "MD023" # Headers must start at the beginning of the line
rule "MD024", :allow_different_nesting => false # Multiple headers with the same content
rule "MD025", :level => 1 # Multiple top level headers in the same document
rule "MD026", :punctuation => ".,;:!?" # Trailing punctuation in header
rule "MD027" # Multiple spaces after blockquote symbol
rule "MD028" # Blank line inside blockquote
rule "MD029", :style => :ordered # Ordered list item prefix
rule "MD030", :ul_single => 1, :ol_single => 1, :ul_multi => 1, :ol_multi => 1 # Spaces after list markers
rule "MD031" # Fenced code blocks should be surrounded by blank lines
rule "MD032" # Lists should be surrounded by blank lines
rule "MD033" # Inline HTML
rule "MD034" # Bare URL used
rule "MD035", :style => "---" # Horizontal rule style
rule "MD036", :punctuation => ".,;:!?" # Emphasis used instead of a header
rule "MD037" # Spaces inside emphasis markers
rule "MD038" # Spaces inside code span elements
rule "MD039" # Spaces inside link text
rule "MD040" # Fenced code blocks should have a language specified
rule "MD041", :level => 1 # First line in file should be a top level header
rule "MD046", :style => :fenced # Code block style
