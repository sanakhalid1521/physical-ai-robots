import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import frontmatter  # This will be installed as part of markdown processing
import markdown
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def load_markdown_file(file_path: str) -> Dict[str, Any]:
    """
    Load a markdown file and extract its content and metadata.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary containing 'content', 'metadata', and 'title'
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        content = post.content
        metadata = post.metadata

    # Extract title from metadata or from the first heading
    title = metadata.get('title', '')
    if not title:
        # Look for first heading in content
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('## '):
                title = line[3:].strip()
                break

    return {
        'content': content,
        'metadata': metadata,
        'title': title or Path(file_path).stem
    }


def load_all_markdown_files(directory_path: str) -> List[Dict[str, Any]]:
    """
    Load all markdown files from a directory recursively.

    Args:
        directory_path: Path to the directory containing markdown files

    Returns:
        List of dictionaries containing content and metadata for each file
    """
    markdown_files = []
    directory = Path(directory_path)

    for md_file in directory.rglob('*.md'):
        try:
            file_data = load_markdown_file(str(md_file))
            file_data['source_file'] = str(md_file)
            markdown_files.append(file_data)
            logger.info(f"Loaded markdown file: {md_file}")
        except Exception as e:
            logger.error(f"Failed to load markdown file {md_file}: {e}")

    return markdown_files


def extract_headings(content: str) -> List[Dict[str, Any]]:
    """
    Extract headings from markdown content.

    Args:
        content: Markdown content to extract headings from

    Returns:
        List of dictionaries containing heading level, text, and position
    """
    headings = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match markdown headings (# ## ### etc.)
        heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            headings.append({
                'level': level,
                'text': text,
                'line_number': i,
                'position': len('\n'.join(lines[:i]))  # Character position
            })

    return headings


def split_by_headings(content: str) -> List[Dict[str, Any]]:
    """
    Split content by headings to create logical sections.

    Args:
        content: Markdown content to split

    Returns:
        List of sections with content and heading information
    """
    lines = content.split('\n')
    sections = []
    current_section = {'heading': '', 'content': '', 'start_line': 0, 'end_line': 0}

    for i, line in enumerate(lines):
        heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            # If we have a current section with content, save it
            if current_section['content'].strip():
                current_section['end_line'] = i - 1
                sections.append(current_section)

            # Start a new section
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            current_section = {
                'heading': heading_text,
                'content': f"{line}\n",  # Include the heading line
                'start_line': i,
                'end_line': i,
                'level': level
            }
        else:
            current_section['content'] += f"{line}\n"

    # Add the last section if it has content
    if current_section['content'].strip():
        current_section['end_line'] = len(lines) - 1
        sections.append(current_section)

    return sections


def clean_markdown_content(content: str) -> str:
    """
    Clean markdown content by removing extra whitespace and normalizing.

    Args:
        content: Raw markdown content

    Returns:
        Cleaned content
    """
    # Remove extra whitespace while preserving paragraph structure
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = content.strip()
    return content


def markdown_to_plain_text(markdown_text: str) -> str:
    """
    Convert markdown to plain text by removing markdown formatting.

    Args:
        markdown_text: Markdown formatted text

    Returns:
        Plain text with markdown formatting removed
    """
    # Convert markdown to HTML first
    html = markdown.markdown(markdown_text)
    # Then extract text from HTML
    soup = BeautifulSoup(html, 'html.parser')
    plain_text = soup.get_text()
    # Clean up extra whitespace
    plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
    plain_text = plain_text.strip()
    return plain_text


def process_book_chapters(directory_path: str) -> List[Dict[str, Any]]:
    """
    Process all markdown files in a directory as book chapters.

    Args:
        directory_path: Path to directory containing book chapters as markdown files

    Returns:
        List of processed chapters with content, metadata, and structure information
    """
    chapters = load_all_markdown_files(directory_path)

    processed_chapters = []
    for i, chapter in enumerate(chapters):
        # Extract headings to understand the structure
        headings = extract_headings(chapter['content'])
        sections = split_by_headings(chapter['content'])

        processed_chapters.append({
            'id': f"chapter_{i:03d}_{Path(chapter['source_file']).stem}",
            'title': chapter['title'],
            'content': clean_markdown_content(chapter['content']),
            'source_file': chapter['source_file'],
            'metadata': chapter['metadata'],
            'headings': headings,
            'sections': sections,
            'word_count': len(chapter['content'].split()),
            'char_count': len(chapter['content'])
        })

    # Sort chapters by filename to maintain order
    processed_chapters.sort(key=lambda x: x['source_file'])

    # Add chapter numbers
    for i, chapter in enumerate(processed_chapters):
        chapter['chapter_number'] = i + 1

    return processed_chapters


def validate_markdown_content(content: str) -> List[str]:
    """
    Validate markdown content for common issues.

    Args:
        content: Markdown content to validate

    Returns:
        List of validation issues found
    """
    issues = []

    # Check for unmatched code blocks
    code_block_count = content.count('```')
    if code_block_count % 2 != 0:
        issues.append("Unmatched code block delimiters")

    # Check for unmatched inline code
    lines = content.split('\n')
    for i, line in enumerate(lines):
        inline_code_matches = re.findall(r'`[^`]*$', line)
        if inline_code_matches:
            issues.append(f"Unmatched inline code on line {i + 1}")

    # Check for reference-style links without definitions
    ref_links = re.findall(r'\[([^\]]+)\]\[([^\]]*)\]', content)
    for link_text, ref_id in ref_links:
        if not ref_id:
            ref_id = link_text
        link_defs = re.findall(r'^\[([^\]]+)\]:', content, re.MULTILINE)
        if ref_id not in link_defs:
            issues.append(f"Undefined reference link: {ref_id}")

    return issues