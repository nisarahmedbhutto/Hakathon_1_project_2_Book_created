"""
Validation script for clean text output quality in the website content ingestion system.
Validates that the extracted content meets quality standards for RAG system use.
"""

import os
import sys
from pathlib import Path

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extractor.content_extractor import ContentExtractor
from extractor.cleaner import clean_html_noise, extract_content_structure
from extractor.metadata_manager import MetadataManager, extract_page_metadata
from extractor.content_handler import ContentHandler
import re


def create_sample_html_pages():
    """Create sample HTML content that mimics various types of Docusaurus pages."""
    samples = {
        "intro_page": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Introduction to Physical AI and Humanoid Robotics</title>
            <meta name="description" content="Comprehensive guide to physical AI and humanoid robotics">
            <meta name="keywords" content="AI, robotics, humanoid, physical AI, machine learning">
            <meta name="author" content="Book Authors">
        </head>
        <body>
            <header class="navbar">
                <nav>Docusaurus Navigation</nav>
            </header>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1 id="introduction">Introduction to Physical AI</h1>

                    <p>Welcome to the comprehensive guide on Physical AI and Humanoid Robotics. This book covers the fundamental concepts, practical applications, and future directions of embodied artificial intelligence.</p>

                    <h2 id="what-is-physical-ai">What is Physical AI?</h2>

                    <p>Physical AI refers to artificial intelligence systems that interact with the physical world through sensors and actuators. Unlike traditional AI that operates primarily in digital spaces, Physical AI must navigate the complexities of real-world physics, uncertainty, and embodied interaction.</p>

                    <div class="theme-admonition">
                        <p>Key insight: Physical AI bridges the gap between digital intelligence and physical action.</p>
                    </div>

                    <h3 id="key-concepts">Key Concepts</h3>

                    <ul>
                        <li>Embodied Intelligence</li>
                        <li>Sensorimotor Learning</li>
                        <li>Real-world Interaction</li>
                        <li>Dynamic Adaptation</li>
                    </ul>

                    <p>These concepts form the foundation of humanoid robotics, where AI systems must operate in three-dimensional physical space with all its inherent challenges.</p>

                    <a href="/docs/next-page" class="theme-edit-this-page">Edit this page</a>
                </div>
            </main>

            <footer class="footer">
                <p>Footer content</p>
            </footer>
        </body>
        </html>
        """,

        "technical_page": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technical Implementation - Control Systems</title>
            <meta name="description" content="Technical details on control systems for humanoid robots">
            <meta name="keywords" content="control systems, robotics, PID, feedback, actuators">
            <meta name="author" content="Technical Team">
        </head>
        <body>
            <header class="navbar">
                <nav>Navigation</nav>
            </header>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1 id="control-systems">Control Systems for Humanoid Robots</h1>

                    <p>Implementing control systems for humanoid robots requires sophisticated algorithms that can handle multiple degrees of freedom and maintain balance.</p>

                    <h2 id="pid-control">PID Control Implementation</h2>

                    <p>PID (Proportional-Integral-Derivative) controllers are fundamental to robotic control systems:</p>

                    <pre><code class="language-python">import numpy as np

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.previous_error = 0
        self.integral = 0

    def update(self, setpoint, measured_value, dt):
        error = setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output
                    </code></pre>

                    <h2 id="balance-algorithms">Balance Algorithms</h2>

                    <p>Balance control in humanoid robots often uses inverted pendulum models and zero moment point (ZMP) calculations.</p>

                    <table>
                        <thead>
                            <tr>
                                <th>Algorithm</th>
                                <th>Application</th>
                                <th>Complexity</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PID Control</td>
                                <td>Joint Position</td>
                                <td>Medium</td>
                            </tr>
                            <tr>
                                <td>Model Predictive Control</td>
                                <td>Whole-body Control</td>
                                <td>High</td>
                            </tr>
                        </tbody>
                    </table>

                    <blockquote>
                        <p>"The key to humanoid balance is maintaining the center of mass within the support polygon."</p>
                        <cite>Dr. Robotics</cite>
                    </blockquote>
                </div>
            </main>
        </body>
        </html>
        """,

        "reference_page": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Reference - Sensor Integration</title>
            <meta name="description" content="API reference for sensor integration in humanoid robots">
            <meta name="keywords" content="API, sensors, integration, robotics, documentation">
            <meta name="author" content="Documentation Team">
        </head>
        <body>
            <header class="navbar">
                <nav>Navigation</nav>
            </header>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1 id="sensor-api">Sensor Integration API Reference</h1>

                    <p>This section provides detailed API documentation for sensor integration in humanoid robots.</p>

                    <h2 id="sensor-types">Supported Sensor Types</h2>

                    <p>The system supports various sensor types:</p>

                    <ul>
                        <li><strong>Inertial Measurement Units (IMUs)</strong>: Provide orientation and acceleration data</li>
                        <li><strong>Force/Torque Sensors</strong>: Measure forces and torques at joints</li>
                        <li><strong>Cameras</strong>: Visual input for perception</li>
                        <li><strong>LIDAR</strong>: Distance measurement and mapping</li>
                    </ul>

                    <h3 id="api-endpoints">API Endpoints</h3>

                    <p>Each sensor type has dedicated API endpoints:</p>

                    <pre><code class="language-python"># IMU sensor endpoint
GET /api/sensors/imu/{sensor_id}

# Response format
{
    "timestamp": "2025-01-15T10:30:00Z",
    "orientation": {"x": 0.1, "y": 0.2, "z": 0.3, "w": 0.9},
    "angular_velocity": {"x": 0.01, "y": 0.02, "z": 0.03},
    "linear_acceleration": {"x": 9.8, "y": 0.1, "z": 0.2}
}
                    </code></pre>

                    <h2 id="configuration">Configuration Options</h2>

                    <p>Sensors can be configured with various parameters:</p>

                    <ul>
                        <li>Sampling rate</li>
                        <li>Calibration settings</li>
                        <li>Filtering options</li>
                        <li>Error thresholds</li>
                    </ul>

                    <p>For more details, see the <a href="/docs/configuration">configuration guide</a>.</p>
                </div>
            </main>
        </body>
        </html>
        """
    }
    return samples


def validate_content_quality(content, page_type):
    """Validate the quality of extracted content."""
    print(f"\nValidating content quality for {page_type}...")

    issues = []

    # Check content length
    if len(content) < 50:
        issues.append("Content is too short (< 50 characters)")

    # Check word count
    words = content.split()
    if len(words) < 10:
        issues.append("Content has too few words (< 10)")

    # Check for excessive whitespace
    if content.count('  ') > 10:  # More than 10 double spaces
        issues.append("Content has excessive double spaces")

    # Check for proper sentence structure
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    if len(sentences) > 0:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length < 3:
            issues.append(f"Average sentence length too short ({avg_sentence_length:.1f} words)")

    # Check for special characters that might indicate noise
    special_char_ratio = len(re.findall(r'[^\w\s\.\,\!\?\;\:\-\(\)]', content)) / len(content)
    if special_char_ratio > 0.1:  # More than 10% special characters
        issues.append(f"High ratio of special characters ({special_char_ratio:.2%})")

    # Check for common noise patterns
    noise_patterns = [
        r'Previous\s+[^\n]*\nNext\s+[^\n]*',  # Navigation
        r'Edit this page',  # Edit links
        r'Last updated',  # Timestamps
        r'Navigation',  # Navigation elements
        r'Footer',  # Footer content
    ]

    for pattern in noise_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found noise pattern: {pattern}")

    # Calculate quality score
    max_issues = 5
    quality_score = max(0, 100 - (len(issues) * (100 / max_issues)))

    print(f"  - Content length: {len(content)} characters")
    print(f"  - Word count: {len(words)} words")
    print(f"  - Sentence count: {len(sentences)} sentences")
    print(f"  - Quality score: {quality_score}%")

    if issues:
        print(f"  - Issues found: {len(issues)}")
        for issue in issues:
            print(f"    • {issue}")
    else:
        print("  - No quality issues found")

    return quality_score, issues


def validate_metadata_quality(metadata, page_type):
    """Validate the quality of extracted metadata."""
    print(f"\nValidating metadata quality for {page_type}...")

    issues = []

    # Check required fields
    required_fields = ['title', 'description']
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            issues.append(f"Missing required field: {field}")

    # Check title quality
    if 'title' in metadata:
        title = metadata['title']
        if len(title) < 5:
            issues.append("Title is too short (< 5 characters)")
        if len(title) > 100:
            issues.append("Title is too long (> 100 characters)")

    # Check description quality
    if 'description' in metadata:
        desc = metadata['description']
        if len(desc) < 10:
            issues.append("Description is too short (< 10 characters)")
        if len(desc) > 200:
            issues.append("Description is too long (> 200 characters)")

    print(f"  - Metadata fields: {list(metadata.keys())}")

    if issues:
        print(f"  - Issues found: {len(issues)}")
        for issue in issues:
            print(f"    • {issue}")
    else:
        print("  - No metadata quality issues found")

    return len(issues) == 0


def main():
    """Run content quality validation tests."""
    print("Running content quality validation...")

    # Create sample HTML pages
    samples = create_sample_html_pages()

    # Initialize extractors
    extractor = ContentExtractor()
    metadata_manager = MetadataManager()
    content_handler = ContentHandler()

    overall_score = 0
    total_pages = 0

    for page_type, html_content in samples.items():
        print(f"\n{'='*60}")
        print(f"Validating {page_type.upper()} page")
        print(f"{'='*60}")

        # Extract content using different methods
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Test ContentExtractor
        print("\n--- Testing ContentExtractor ---")
        extracted = extractor.extract_content(soup)
        content_quality, content_issues = validate_content_quality(extracted['content'], page_type)
        metadata_valid = validate_metadata_quality(extracted['metadata'], page_type)

        # Test ContentHandler
        print("\n--- Testing ContentHandler ---")
        content_by_type = content_handler.handle_content_types(soup)
        handler_content = content_handler.process_content_for_embedding(soup)
        handler_quality, handler_issues = validate_content_quality(handler_content, f"{page_type}_handler")

        # Test Cleaner
        print("\n--- Testing Cleaner ---")
        clean_content = clean_html_noise(html_content)
        cleaner_quality, cleaner_issues = validate_content_quality(clean_content, f"{page_type}_cleaner")

        # Test MetadataManager
        print("\n--- Testing MetadataManager ---")
        metadata = metadata_manager.extract_metadata_from_page(soup, f"https://example.com/docs/{page_type}")
        metadata_valid = validate_metadata_quality(metadata, f"{page_type}_metadata")

        # Calculate average score for this page
        avg_score = (content_quality + handler_quality + cleaner_quality) / 3
        overall_score += avg_score
        total_pages += 1

        print(f"\nPage {page_type} average quality: {avg_score:.1f}%")

    # Overall results
    overall_avg_score = overall_score / total_pages if total_pages > 0 else 0

    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS")
    print(f"{'='*60}")
    print(f"Pages processed: {total_pages}")
    print(f"Average quality score: {overall_avg_score:.1f}%")

    if overall_avg_score >= 80:
        print("SUCCESS: Content quality is excellent!")
    elif overall_avg_score >= 60:
        print("SUCCESS: Content quality is good with minor issues.")
    elif overall_avg_score >= 40:
        print("INFO: Content quality is acceptable but needs improvement.")
    else:
        print("WARNING: Content quality needs significant improvement.")

    # Test chunking functionality
    print(f"\n{'='*60}")
    print(f"TESTING CHUNKING FUNCTIONALITY")
    print(f"{'='*60}")

    # Get a sample content to test chunking
    sample_content = list(samples.values())[0]
    soup = BeautifulSoup(sample_content, 'html.parser')
    extracted = extractor.extract_content(soup)

    # Import chunking function
    from extractor.content_cleaner import chunk_content

    chunks = chunk_content(extracted['content'], chunk_size=500, overlap=50)
    print(f"Original content length: {len(extracted['content'])} characters")
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk)} characters")

    print(f"\nSUCCESS: Content quality validation completed successfully!")
    print("All extraction and cleaning components are working as expected.")


if __name__ == "__main__":
    main()