import asyncio
from google.cloud import firestore

async def listen_for_changes():
    db = firestore.AsyncClient()

    async def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f'Document data: {doc.to_dict()}')

    doc_ref = db.collection('your_collection').document('your_document_id')
    doc_watch = doc_ref.on_snapshot(on_snapshot)

    # Giữ cho vòng lặp lắng nghe thay đổi chạy liên tục
    while True:
        await asyncio.sleep(1)

async def main():
    # Chạy lắng nghe thay đổi trong một task
    asyncio.create_task(listen_for_changes())

    # Thực hiện các tác vụ khác trong vòng lặp chính
    while True:
        # Thực hiện tác vụ khác ở đây
        await asyncio.sleep(10)  # Ví dụ: Đọc dữ liệu mỗi 10 giây

# Chạy chương trình
asyncio.run(main())
