import numpy as np,uuid,datetime
def route_memory(content,phase="discovery"):
    scores={"archivist":0.2,"formalist":0.2,"synthesist":0.3,"strategist":0.3}
    w=np.array(list(scores.values()))
    w=w/w.sum()
    weighted=dict(zip(scores.keys(),w))
    primary=max(weighted,key=weighted.get)
    return {"memory_id":str(uuid.uuid4()),"routing":{"primary_owner":primary,"weights":weighted},"created_at":datetime.datetime.utcnow().isoformat()}
