# Agentic Design Patterns - Book to App

Converting the book "Agentic Design Patterns" into a functional application and accessible markdown format.

## Overview

This repository contains the complete "Agentic Design Patterns" book converted from Microsoft Word (.docx) format to markdown (.md) format, making it more accessible for developers and suitable for integration into applications.

## Repository Structure

```
.
├── book/                    # Original .docx files
├── book_md/                 # Converted markdown files
├── images/                  # Extracted images from the book
├── convert_docx_to_markdown.py  # Conversion script
└── README.md
```

## Book Contents

The book covers 21 chapters on agentic design patterns, plus appendices:

### Core Patterns
1. **Chapter 1**: Prompt Chaining
2. **Chapter 2**: Routing
3. **Chapter 3**: Parallelization
4. **Chapter 4**: Reflection
5. **Chapter 5**: Tool Use
6. **Chapter 6**: Planning
7. **Chapter 7**: Multi-Agent Collaboration
8. **Chapter 8**: Memory Management
9. **Chapter 9**: Learning and Adaptation
10. **Chapter 10**: Model Context Protocol (MCP)

### Advanced Patterns
11. **Chapter 11**: Goal Setting and Monitoring
12. **Chapter 12**: Exception Handling and Recovery
13. **Chapter 13**: Human-in-the-Loop
14. **Chapter 14**: Knowledge Retrieval (RAG)
15. **Chapter 15**: Inter-Agent Communication (A2A)
16. **Chapter 16**: Resource-Aware Optimization
17. **Chapter 17**: Reasoning Techniques
18. **Chapter 18**: Guardrails/Safety Patterns
19. **Chapter 19**: Evaluation and Monitoring
20. **Chapter 20**: Prioritization
21. **Chapter 21**: Exploration and Discovery

### Appendices
- **Appendix A**: Advanced Prompting Techniques
- **Appendix B**: AI Agentic Interactions - From GUI to Real World Environment
- **Appendix C**: Quick Overview of Agentic Frameworks
- **Appendix D**: Building an Agent with AgentSpace
- **Appendix E**: AI Agents on the CLI
- **Appendix F**: Under the Hood - An Inside Look at the Agents' Reasoning Engines
- **Appendix G**: Coding Agents

## Conversion Features

The conversion script (`convert_docx_to_markdown.py`) handles:
- ✅ **Text Formatting**: Preserves bold formatting, removes italic formatting
- ✅ **Lists**: Properly distinguishes between bulleted and numbered lists
- ✅ **Code Blocks**: Extracts Python code from 1x1 tables into proper code blocks
- ✅ **Images**: Extracts all images and creates proper markdown references
- ✅ **Tables**: Converts multi-cell tables to markdown table format
- ✅ **Paragraph Breaks**: Handles paragraph breaks correctly for proper list numbering
- ✅ **Headings**: Maintains document structure with proper heading levels

## Usage

### Prerequisites

```bash
pip install -r requirements.txt
```

### Converting the Book

To convert the .docx files to markdown:

```bash
python convert_docx_to_markdown.py
```

The script will:
1. Read all .docx files from the `book/` directory
2. Extract images to the `images/` directory
3. Convert content to markdown in the `book_md/` directory

### Reading the Markdown Files

The converted markdown files can be:
- Viewed directly on GitHub
- Opened in any markdown editor
- Integrated into documentation systems
- Used as input for AI/LLM applications

## Future Development

This repository aims to transform the static book content into an interactive application that demonstrates the agentic design patterns in action. Planned features include:

- [ ] Interactive demos for each design pattern
- [ ] Code examples that can be run directly
- [ ] Web-based interface for exploring patterns
- [ ] API for integrating patterns into other applications
- [ ] Jupyter notebooks with practical exercises

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Improving the conversion process
- Adding interactive demonstrations
- Creating practical examples
- Enhancing documentation
- Building the web application

## License

Please refer to the original book's license terms. The conversion scripts in this repository are provided as-is for educational purposes.

## Acknowledgments

- Original book authors for creating comprehensive content on agentic design patterns
- Contributors to the conversion and application development efforts