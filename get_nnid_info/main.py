from nintendo import nnas
import settings
import asyncio

async def main():
    cfg = settings.Settings().load()
    nas = nnas.NNASClient()

    try:
        nnid = await nas.get_nnid(cfg["pid"])
    except KeyError:
        nnid = None
        print(f"⚠️  PID {cfg['pid']} not found")

    try:
        pid = await nas.get_pid(cfg["nnid"])
    except KeyError:
        pid = None
        print(f"⚠️  NNID {cfg['nnid']} not found")

    print("NNID:", nnid)
    print("PID:", pid)



asyncio.run(main())
