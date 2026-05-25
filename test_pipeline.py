import traceback

try:
    from pipeline import adapt_contract

    with open('05_test_contract_CN.docx', 'rb') as f:
        file_bytes = f.read()

    print("File loaded, calling adapt_contract...")

    result = adapt_contract(
        file_bytes=file_bytes,
        file_ext='docx',
        corridor='CN_SG',
        doc_type='employment_contract',
        company_name='Test Company Pte. Ltd.'
    )

    print('=== SECTIONS RETURNED ===')
    print(f'clean:       {len(result["clean"])} chars')
    print(f'redline:     {len(result["redline"])} chars')
    print(f'commentary:  {len(result["commentary"])} chars')
    print()
    print('--- CLEAN (first 300 chars) ---')
    print(result['clean'][:300])

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()