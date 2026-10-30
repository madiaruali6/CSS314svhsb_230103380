import sys, time
from multiprocessing import Process, Queue


def buffered_worker(out_queue, items_per_worker, batch_size=10_000):
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))  # one flush per 10,000 items
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)  # sentinel


def run_buffered(p, total_items=10_000_000):
    q = Queue()
    items_per_worker = total_items // p
    workers = [Process(target=buffered_worker, args=(q, items_per_worker)) for _ in range(p)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    total_sum, active = 0, p
    while active > 0:
        val = q.get()
        if val is None:
            active -= 1
        else:
            total_sum += val
    for w in workers:
        w.join()
    return time.perf_counter() - t0, total_sum


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000
    cores = [1, 2, 4, 8]
    res = {p: run_buffered(p, total) for p in cores}
    t1 = res[1][0]
    print(f"P= 1 | Time={t1:6.3f}s | sum={res[1][1]}")
    print("\n--- Buffered Karp-Flatt Analysis ---")
    for p in [2, 4, 8]:
        tp, s = res[p]
        e = ((p * tp / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={t1/tp:5.2f}x | Karp-Flatt e={e:6.3f} | sum={s}")
