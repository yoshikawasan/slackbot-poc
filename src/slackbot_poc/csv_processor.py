import pandas as pd
import io
from typing import List, Union


def validate_csv_format(file_content: bytes) -> bool:
    """Validate if the file content is a valid CSV with comma separation."""
    try:
        content_str = file_content.decode('utf-8')
        if not content_str.strip():
            return False
        df = pd.read_csv(io.StringIO(content_str))
        return len(df.columns) > 0 and not all(col.startswith('Unnamed:') for col in df.columns)
    except Exception:
        return False


def check_comma_separation(file_content: bytes) -> bool:
    """Check if CSV uses comma separation by attempting to detect delimiter."""
    try:
        content_str = file_content.decode('utf-8')
        sample_lines = content_str.split('\n')[:5]
        
        for line in sample_lines:
            if line.strip():
                if ',' not in line:
                    return False
                if ';' in line or '\t' in line:
                    comma_count = line.count(',')
                    semi_count = line.count(';')
                    tab_count = line.count('\t')
                    if semi_count > comma_count or tab_count > comma_count:
                        return False
        return True
    except Exception:
        return False


def process_csv_files(file_contents: List[bytes]) -> Union[str, List[str]]:
    """Process multiple CSV files and double integer values."""
    results = []
    
    for i, file_content in enumerate(file_contents):
        if not validate_csv_format(file_content):
            return "Please send csv file"
        
        if not check_comma_separation(file_content):
            return "Please send csv file with comma(,)."
    
    for i, file_content in enumerate(file_contents):
        try:
            content_str = file_content.decode('utf-8')
            df = pd.read_csv(io.StringIO(content_str))
            
            for col in df.columns:
                if df[col].dtype in ['int64', 'int32', 'int16', 'int8']:
                    df[col] = df[col] * 2
            
            output = io.StringIO()
            df.to_csv(output, index=False)
            results.append(output.getvalue())
            
        except Exception as e:
            return f"Error processing file {i+1}: {str(e)}"
    
    return results


def format_results_for_slack(results: List[str]) -> str:
    """Format processed CSV results for Slack message."""
    if len(results) == 1:
        return f"```\n{results[0]}\n```"
    
    formatted = []
    for i, result in enumerate(results):
        formatted.append(f"**File {i+1}:**\n```\n{result}\n```")
    
    return "\n\n".join(formatted)