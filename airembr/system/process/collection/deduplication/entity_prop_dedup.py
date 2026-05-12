class PropertyDeduper:
    def __init__(self):
        self.latest = {}

    def process(self, changes):
        changed_keys = set()

        for record in changes:
            key = (
                record["entity.pk"],
                record["property.name"],
                record["property.value"],
            )

            ts = record["ts"]

            if key not in self.latest:
                rec = record.copy()
                rec["count"] = 1
                self.latest[key] = rec
                changed_keys.add(key)
            else:
                existing = self.latest[key]
                existing["count"] += 1

                # mark as changed even if ts is older
                changed_keys.add(key)

                if ts > existing["ts"]:
                    count = existing["count"]
                    rec = record.copy()
                    rec["count"] = count
                    self.latest[key] = rec

        # ✅ only return records touched in this batch
        return [self.latest[k] for k in changed_keys]
