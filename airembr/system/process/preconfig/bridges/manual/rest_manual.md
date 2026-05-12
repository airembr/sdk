# REST API Manual – Collection Bridge

This API allows your backend to collect observation data in a structured JSON format using the __POST /__ endpoint. It is designed to capture user actions, context, metadata, and consent in a unified schema.

---

## Overview

* **Protocol**: HTTPS
* **Content Type**: __application/json; charset=utf-8__
* **Endpoint**: __POST /__
* **Purpose**: Submit observation events describing user behavior, entity relationships, metadata, and consents.

---

## Endpoint Specification

### __POST /__

Ingest a new **Observation** document.

| Attribute    | Value                                                                                   |
| ------------ | --------------------------------------------------------------------------------------- |
| **Method**   | __POST__                                                                                  |
| **Path**     | __/__                                                                          |
| **Consumes** | __application/json; charset=utf-8__                                                       |
| **Produces** | __application/json__                                                                      |
| **Success**  | __201 Created__ with response body __{"id": "<observation-id>"}__                           |
| **Failure**  | __400 Bad Request__ (validation error), __422__ (invalid content type), __500__ (server error) |

---

## Request Body Schema (Simplified)

```jsonc
{
  "id": "obs-123",               // Optional: auto-generated if omitted
  "name": "purchase-checkout",   // Optional: name of the observation
  "aspect": "e-commerce",        // Optional: data category or theme

  "source": {
    "id": "shop-42",
    "type": "shop",
    "name": "MegaShop"
  },

  "entities": {
    "actor-1": {
      "instance": "user #1",
      "traits": { "email": "a@example.com" }
    },
    "product-1": {
      "instance": "product #1",
      "traits": { "title": "Red Sneakers", "price": 79.9 }
    }
  },

  "relation": [
    {
      "label": "bought",
      "actor": "actor-1",
      "objects": ["product-1"],
      "traits": { "quantity": 1 },
      "semantic": {
        "summary": "{{actor}} bought {{object}}.",
        "description": "{{actor}} purchased {{object}} via checkout V2."
      }
    }
  ],

  "metadata": {
    "application": { "name": "web-shop", "version": "2.4.1" },
    "device": { "id": "device-hash-abc", "ip": "1.2.3.4", "mobile": false },
    "os": { "name": "Windows", "version": "11" },
    "location": {
      "country": { "code": "PL", "name": "Poland" },
      "city": "Warsaw"
    }
  },

  "consents": ["metrics", "marketing"],
  "aux": { "checkout_version": "v2" }
}
```

---

### Field Reference

| Field      | Description                                                                                                                                                                                                                            |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| __id__       | Optional. If not provided, the server will assign a value in the form __anon-<uuid>__.                                                                                                                                                   |
| __name__     | Optional name for the observation (e.g., "purchase-checkout").                                                                                                                                                                         |
| __aspect__   | Optional tag for grouping observations by domain or partition.                                                                                                                                                                         |
| __source__   | Identifies the origin of the observation (e.g., app, store, sensor). Requires __id__, optional __type__ and __name__.                                                                                                                        |
| __entities__ | Dictionary of entities participating in the observation. Keys are aliases (like __actor-1__, __product-1__). Values contain __instance__, optional __traits__, and possibly hierarchy or per-entity consent.                                   |
| __relation__ | Required. Describes the observed action, with:<br>• __label__: verb or event type<br>• __actor__: reference to an entity alias<br>• __objects__: zero or more entity aliases<br>• Optional __traits__, __tags__, __semantic__ rendering templates. |
| __metadata__ | Optional. Application, device, OS, and location data collected at the point of observation.                                                                                                                                            |
| __consents__ | Optional. List of granted user consents. If omitted, consent is assumed (__allow=true__).                                                                                                                                                |
| __aux__      | Optional. A flexible structure for additional non-standard fields.                                                                                                                                                                     |

---

### Server-Side Behavior

* **Automatic ID Generation**: If no __id__ is provided, the server assigns a random UUID prefixed with __anon-__.
* **Semantic Rendering**: If a __semantic__ block is present in a relation, the server replaces placeholders (e.g., __{actor}__) with resolved names during storage (e.g., *“Anna bought Red Sneakers”*).

---

## Example Request

```bash
curl -X POST https://api.your-domain.com/ \
  -H 'Content-Type: application/json' \
  -d '{
    "source": { "id": "shop-42" },
    "entities": {
      "actor-1": {
        "instance": "person #123",
        "traits": { "name": "Anna" }
      }
    },
    "relation": [
      {
        "type": "event",
        "label": "viewed-page",
        "actor": "actor-1",
        "traits": { "url": "http://localhost" }
      }
    ]
  }'
```

### Expected Response

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "obs-456"
}
```

---

## Notes

* Entities and relations must reference each other using the same aliases defined in __entities__.
* You may submit multiple __objects__ in a relation.
* Consent management is centralized per observation, but you may add per-entity consents too.
* Keep trait structures flat or use dot-notation for nested structures.


