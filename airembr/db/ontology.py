ontology = [
  {
    "type": "person",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A person: alive, dead, undead, or fictional.",
    "ref": {
      "@location": {
        "description": "Where the person is currently located.",
        "relation": "location",
        "verb": "has"
      },
      "@address": {
        "description": "Postal address where the person resided.",
        "relation": "address",
        "verb": "has"
      },
      "@country": {
        "description": "Country of the person's citizenship or nationality.",
        "relation": "nationality",
        "verb": "has"
      },
      "@email_address": {
        "description": "Email addresses belonging to the person.",
        "relation": "email",
        "verb": "has"
      },
      "@phone_number": {
        "description": "Phone numbers belonging to the person.",
        "relation": "phone",
        "verb": "has"
      },
      "@document": {
        "description": "Documents the person authored or owned.",
        "relation": "document",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources the person created or owns.",
        "relation": "resource",
        "verb": "has"
      },
      "@message": {
        "description": "Messages the person sent or received.",
        "relation": "message",
        "verb": "has"
      },
      "@health": {
        "description": "Health records about the person.",
        "relation": "health_record",
        "verb": "has"
      },
      "@category": {
        "description": "Categories or tags applied to the person.",
        "relation": "category",
        "verb": "has"
      },
      "@sentiment": {
        "description": "Sentiment expressed toward the person.",
        "relation": "sentiment",
        "verb": "has"
      }
    },
    "properties": {
      "$type": "Relation to observer: friend, family, bystander, sender, recipient, etc.",
      "$first_name": "First name.",
      "$last_name": "Family name.",
      "$email": "Email address.",
      "$phone": "Phone number.",
      "$nationality": "Person nationality",
      "$birth_date": "Date of birth (ISO 8601).",
      "$label": "Display name: $first_name or $first_name + $last_name."
    }
  },
  {
    "type": "organization",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A group of people acting under a shared identity or purpose.",
    "ref": {
      "@email_address": {
        "description": "Email addresses belonging to the organization.",
        "relation": "email",
        "verb": "has"
      },
      "@phone_number": {
        "description": "Phone numbers belonging to the organization.",
        "relation": "phone",
        "verb": "has"
      },
      "@location": {
        "description": "Where the organization is based or operates.",
        "relation": "location",
        "verb": "has"
      },
      "@address": {
        "description": "Postal addresses of the organization.",
        "relation": "address",
        "verb": "has"
      },
      "@country": {
        "description": "Country of registration or primary jurisdiction.",
        "relation": "jurisdiction",
        "verb": "has"
      },
      "@person": {
        "description": "People affiliated with the organization (members, staff).",
        "relation": "member",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources owned or published by the organization.",
        "relation": "resource",
        "verb": "has"
      },
      "@document": {
        "description": "Documents produced by the organization.",
        "relation": "document",
        "verb": "has"
      },
      "@message": {
        "description": "Messages the organization sent or received.",
        "relation": "message",
        "verb": "has"
      },
      "@product": {
        "description": "Products the organization makes or sells.",
        "relation": "product",
        "verb": "has"
      },
      "@category": {
        "description": "Categories or tags applied to the organization.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the organization.",
        "relation": "aspect",
        "verb": "has"
      },
      "@sentiment": {
        "description": "Sentiment expressed toward the organization.",
        "relation": "sentiment",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "The organization's name.",
      "$type": "Type of organization: company, nonprofit, government, etc.",
      "$industry": "Industry or sector.",
      "$website": "Primary website URL.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "country",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A sovereign state or nation — the geopolitical level above organization. Countries hold territory, have citizens and organizations, engage in conflicts and relationships with other countries, and can act as parties in communication.",
    "ref": {
      "@location": {
        "description": "Locations within the country, including its capital.",
        "relation": "location",
        "verb": "has"
      },
      "@conflict": {
        "description": "Conflicts the country is or was party to.",
        "relation": "conflict",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources belonging to the country.",
        "relation": "resource",
        "verb": "has"
      },
      "@document": {
        "description": "Documents issued by the country (treaties, laws).",
        "relation": "document",
        "verb": "has"
      },
      "@message": {
        "description": "Diplomatic messages the country sent or received.",
        "relation": "message",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Common country name (e.g. Poland).",
      "$iso_code": "ISO 3166-1 alpha-2 code (e.g. PL, US, GB).",
      "$region": "Continent or region (e.g. Europe, Asia).",
      "$label": "Display $name ($iso_code)."
    }
  },
  {
    "type": "address",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A physical address in the world. This is not place like, drawer, closet, etc. Real world location.",
    "ref": {
      "@country": {
        "description": "Country this address is in.",
        "relation": "country",
        "verb": "is in"
      }
    },
    "properties": {
      "$type": "Type: city, country, address, region, building, virtual, etc.",
      "$address": "Postal street address.",
      "$city": "City or municipality.",
      "$label": "Display: $address, $city, $country."
    }
  },
  {
    "type": "location",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A physical or virtual place in the world. Virtual locations may have no longitude, latitude, etc.",
    "ref": {
      "@address": {
        "description": "Postal address of this location, if any.",
        "relation": "address",
        "verb": "has"
      },
      "@country": {
        "description": "Country this location sits in.",
        "relation": "country",
        "verb": "is in"
      }
    },
    "properties": {
      "$name": "Location/Place name.",
      "$type": "Type: city, country, address, region, building, virtual, place, etc.",
      "$latitude": "Latitude coordinate.",
      "$longitude": "Longitude coordinate.",
      "$label": "Display name: $name or $address."
    }
  },
  {
    "type": "resource",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "Any resource, online or offline — files, URLs, images, media, and more",
    "ref": {
      "@location": {
        "description": "Where the resource is stored or originates.",
        "relation": "location",
        "verb": "has"
      },
      "@person": {
        "description": "Person who created or owns the resource.",
        "relation": "author",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization that published the resource.",
        "relation": "publisher",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the resource.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Resource title or name.",
      "$type": "Type: file, url, image, video, audio, archive, etc.",
      "$format": "e.g. digital, physical.",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$modified_at": "Last modified timestamp (ISO 8601).",
      "$description": "Short description of the resource content or purpose.",
      "$label": "Display: $name ($type)."
    }
  },
  {
    "type": "document",
    "parent": "resource",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "general",
    "description": "A written or structured artifact conveying information. E.g. contract, order, reservation, receipt, etc.",
    "ref": {
      "@location": {
        "description": "Where the document is stored.",
        "relation": "location",
        "verb": "has"
      },
      "@person": {
        "description": "Person who authored the document.",
        "relation": "author",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization that issued the document.",
        "relation": "issuer",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the document.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Document title.",
      "$type": "Type: report, memo, invoice, receipt, form, article, research paper, driving license, ID, etc.",
      "$format": "e.g. digital, physical.",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$modified_at": "Last modified timestamp (ISO 8601).",
      "$description": "Short description of the document content or purpose.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "email_address",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "communication",
    "description": "An email address.",
    "ref": {},
    "properties": {
      "$type": "Type of address: private, corporate, public (gmail, hotmail, yahoo, etc.), etc.",
      "$address": "The email address string (e.g. user@example.com).",
      "$domain": "The domain part after the @ symbol.",
      "$display_name": "Optional human-readable name associated with the address.",
      "$label": "Display name: $display_name <$address>."
    }
  },
  {
    "type": "phone_number",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "communication",
    "description": "A phone number.",
    "ref": {},
    "properties": {
      "$number": "The full phone number string (e.g. +1 555 123 4567).",
      "$country_code": "International dialing code (e.g. +1, +44).",
      "$extension": "Optional extension number.",
      "$type": "Type of number: mobile, home, work, fax, etc.",
      "$display_name": "Optional human-readable label for the number.",
      "$label": "Display name: $display_name ($type): $number."
    }
  },
  {
    "type": "message",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "communication",
    "description": "A single communication exchanged between parties (person, organization, country) — email, SMS, chat, call, voicemail, letter, etc. Endpoints describe where it was sent; the message captures the content.",
    "ref": {
      "@person": {
        "description": "People who sent or received the message.",
        "relation": "party",
        "verb": "has"
      },
      "@organization": {
        "description": "Organizations that sent or received the message.",
        "relation": "party",
        "verb": "has"
      },
      "@country": {
        "description": "Countries that sent or received the message (diplomatic).",
        "relation": "party",
        "verb": "has"
      },
      "@email_address": {
        "description": "Email endpoints the message was sent from or to.",
        "relation": "endpoint",
        "verb": "has"
      },
      "@phone_number": {
        "description": "Phone endpoints the message was sent from or to.",
        "relation": "endpoint",
        "verb": "has"
      },
      "@resource": {
        "description": "Files attached to the message.",
        "relation": "attachment",
        "verb": "has"
      },
      "@document": {
        "description": "Documents attached to the message.",
        "relation": "attachment",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the message.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$type": "Type: email, sms, chat, call, voicemail, letter, dm, etc.",
      "$channel": "Platform or medium: gmail, whatsapp, slack, sms, phone, letter, diplomatic note, etc.",
      "$subject": "Subject line or title, if applicable.",
      "$summary": "Message summary or transcript.",
      "$sent_at": "When the message was sent (ISO 8601).",
      "$label": "Display name: $type from $sender."
    }
  },
  {
    "type": "meeting",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "interaction",
    "description": "A scheduled or ad-hoc gathering of two or more people. Extends general event.",
    "ref": {
      "@location": {
        "description": "Where the meeting takes place.",
        "relation": "location",
        "verb": "has"
      },
      "@person": {
        "description": "People who attended the meeting.",
        "relation": "attendee",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization that organized the meeting.",
        "relation": "organizer",
        "verb": "has"
      },
      "@country": {
        "description": "Country hosting the meeting.",
        "relation": "host",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources or materials from the meeting.",
        "relation": "resource",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the meeting.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the meeting.",
        "relation": "aspect",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Meeting title or topic.",
      "$type": "Type: in-person, video, phone, async, etc.",
      "$started_at": "Start datetime (ISO 8601).",
      "$ended_at": "End datetime (ISO 8601).",
      "$agenda": "Meeting agenda summary.",
      "$label": "Display: $name ($type) at $started_at."
    }
  },
  {
    "type": "project",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "interaction",
    "description": "A coordinated body of work grouping related tasks toward a shared goal, with its own status and timeline. Parent container for task.",
    "ref": {
      "@person": {
        "description": "Owner and members of the project.",
        "relation": "member",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization responsible for the project.",
        "relation": "owner",
        "verb": "has"
      },
      "@task": {
        "description": "Tasks belonging to the project.",
        "relation": "task",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources used by the project.",
        "relation": "resource",
        "verb": "has"
      },
      "@location": {
        "description": "Where the project is based.",
        "relation": "location",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the project.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the project.",
        "relation": "aspect",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Project name.",
      "$status": "Status: planning, active, on_hold, completed, cancelled.",
      "$started_at": "Start date (ISO 8601).",
      "$due_date": "Target completion date (ISO 8601).",
      "$ended_at": "Actual completion date (ISO 8601).",
      "$description": "Short project description.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "task",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "interaction",
    "description": "A unit of work to be completed by a person or system. May belong to a project.",
    "ref": {
      "@project": {
        "description": "Parent project the task belongs to.",
        "relation": "project",
        "verb": "has"
      },
      "@person": {
        "description": "Person responsible for the task.",
        "relation": "assignee",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization the task belongs to.",
        "relation": "owner",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources needed for the task.",
        "relation": "resource",
        "verb": "has"
      },
      "@document": {
        "description": "Documents related to the task.",
        "relation": "document",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the task.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the task.",
        "relation": "aspect",
        "verb": "has"
      },
      "@location": {
        "description": "Where the task is performed.",
        "relation": "location",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Task title.",
      "$status": "Status: todo, in_progress, blocked, done, cancelled.",
      "$priority": "Priority: low, medium, high, critical.",
      "$due_date": "Due date (ISO 8601).",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$description": "Short task description.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "conflict",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "interaction",
    "description": "A disagreement, dispute, or opposing tension between parties — from interpersonal disputes up to disputes between organizations or countries.",
    "ref": {
      "@person": {
        "description": "People party to the conflict.",
        "relation": "party",
        "verb": "has"
      },
      "@organization": {
        "description": "Organizations party to the conflict.",
        "relation": "party",
        "verb": "has"
      },
      "@country": {
        "description": "Countries party to the conflict.",
        "relation": "party",
        "verb": "has"
      },
      "@document": {
        "description": "Documents related to the conflict.",
        "relation": "document",
        "verb": "has"
      },
      "@location": {
        "description": "Where the conflict takes place.",
        "relation": "location",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the conflict.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the conflict.",
        "relation": "aspect",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Short description of the conflict.",
      "$type": "Type: dispute, disagreement, complaint, legal, negotiation, war, territorial, etc.",
      "$status": "Status: open, escalated, resolved, dismissed.",
      "$started_at": "When the conflict began (ISO 8601).",
      "$resolved_at": "When it was resolved (ISO 8601).",
      "$description": "Full description of the issue.",
      "$resolution": "How it was resolved.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "payment",
    "parent": "document",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "commerce",
    "description": "A financial transaction between parties. Extends document.",
    "ref": {
      "@location": {
        "description": "Where the payment record is stored.",
        "relation": "location",
        "verb": "has"
      },
      "@person": {
        "description": "People involved as payer or payee.",
        "relation": "party",
        "verb": "has"
      },
      "@organization": {
        "description": "Organizations involved as payer or payee.",
        "relation": "party",
        "verb": "has"
      },
      "@order": {
        "description": "Order this payment settles.",
        "relation": "order",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the payment.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Payment reference or title.",
      "$type": "Type: transfer, invoice, subscription, refund, charge, etc.",
      "$format": "e.g. digital, physical.",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$modified_at": "Last modified timestamp (ISO 8601).",
      "$description": "Short description of the payment purpose.",
      "$amount": "Numeric amount.",
      "$currency": "Currency code (ISO 4217), e.g. USD, EUR.",
      "$status": "Status: pending, completed, failed, refunded.",
      "$transacted_at": "Transaction timestamp (ISO 8601).",
      "$reference": "External reference or transaction ID.",
      "$label": "Display name: $type $amount $currency."
    }
  },
  {
    "type": "product",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "commerce",
    "description": "A good or service offered for sale or exchange.",
    "ref": {
      "@organization": {
        "description": "Manufacturer or vendor of the product.",
        "relation": "manufacturer",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources describing the product.",
        "relation": "resource",
        "verb": "has"
      },
      "@location": {
        "description": "Where the product is available.",
        "relation": "availability",
        "verb": "located at"
      },
      "@category": {
        "description": "Categories applied to the product.",
        "relation": "category",
        "verb": "has"
      },
      "@aspect": {
        "description": "Aspects attributed to the product.",
        "relation": "aspect",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Product name.",
      "$type": "Type: physical, digital, subscription, service, etc.",
      "$sku": "Stock keeping unit identifier.",
      "$price": "Unit price.",
      "$currency": "Currency code (ISO 4217).",
      "$description": "Product description.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "order",
    "parent": "document",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "commerce",
    "description": "A formal request to purchase one or more products. Extends document.",
    "ref": {
      "@location": {
        "description": "Delivery or origin location of the order.",
        "relation": "shipping",
        "verb": "located at"
      },
      "@person": {
        "description": "People involved as buyer or seller.",
        "relation": "party",
        "verb": "has"
      },
      "@organization": {
        "description": "Organizations involved as buyer or seller.",
        "relation": "party",
        "verb": "has"
      },
      "@product": {
        "description": "Products ordered as line items.",
        "relation": "item",
        "verb": "has"
      },
      "@payment": {
        "description": "Payment settling the order.",
        "relation": "payment",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the order.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Order title or reference.",
      "$type": "Type: purchase, return, exchange, etc.",
      "$format": "e.g. digital, physical.",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$modified_at": "Last modified timestamp (ISO 8601).",
      "$description": "Short description of the order.",
      "$order_number": "External order identifier.",
      "$status": "Status: draft, placed, shipped, delivered, cancelled, returned.",
      "$total": "Order total amount.",
      "$currency": "Currency code (ISO 4217).",
      "$placed_at": "Order placement timestamp (ISO 8601).",
      "$label": "Display name: Order $order_number."
    }
  },
  {
    "type": "contract",
    "parent": "document",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "commerce",
    "description": "A legally binding agreement between two or more parties. Extends document.",
    "ref": {
      "@location": {
        "description": "Where the contract is stored.",
        "relation": "location",
        "verb": "has"
      },
      "@person": {
        "description": "People who authored or signed the contract.",
        "relation": "signatory",
        "verb": "has"
      },
      "@organization": {
        "description": "Organizations party to the contract.",
        "relation": "signatory",
        "verb": "has"
      },
      "@country": {
        "description": "Countries party to the contract (treaties).",
        "relation": "signatory",
        "verb": "has"
      },
      "@document": {
        "description": "Underlying or related documents.",
        "relation": "document",
        "verb": "has"
      },
      "@payment": {
        "description": "Payments governed by the contract.",
        "relation": "payment",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the contract.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Contract title.",
      "$type": "Type: employment, service, nda, lease, purchase, treaty, etc.",
      "$format": "e.g. digital, physical.",
      "$created_at": "Creation timestamp (ISO 8601).",
      "$modified_at": "Last modified timestamp (ISO 8601).",
      "$description": "Short description of the contract scope.",
      "$status": "Status: draft, active, expired, terminated.",
      "$effective_date": "When it takes effect (ISO 8601).",
      "$expiry_date": "When it expires (ISO 8601).",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "health",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "health",
    "description": "A health-related record, observation, or clinical event for a person.",
    "ref": {
      "@person": {
        "description": "Patient the record concerns (may also be the recording clinician).",
        "relation": "patient",
        "verb": "has"
      },
      "@organization": {
        "description": "Clinic or system that recorded it.",
        "relation": "provider",
        "verb": "has"
      },
      "@document": {
        "description": "Documents supporting the record.",
        "relation": "document",
        "verb": "has"
      },
      "@resource": {
        "description": "Resources attached to the record.",
        "relation": "resource",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the record.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$type": "Record type: condition, observation, medication, procedure, allergy, etc.",
      "$recorded_at": "Timestamp (ISO 8601).",
      "$value": "Measured or observed value, if applicable.",
      "$unit": "Unit of measure, e.g. mg/dL, bpm.",
      "$notes": "Free-text clinical notes.",
      "$label": "Display name: $type for $subject."
    }
  },
  {
    "type": "category",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "abstract",
    "description": "A taxonomy node used to classify, tag, or cluster entities — a category, tag, topic, or label. Categories may nest to form a hierarchy.",
    "ref": {
      "@category": {
        "description": "Parent category in the hierarchy.",
        "relation": "parent",
        "verb": "has"
      }
    },
    "properties": {
      "$name": "Category, tag, or topic name.",
      "$type": "Type: category, tag, topic, label, taxonomy.",
      "$scheme": "Optional taxonomy or namespace this belongs to.",
      "$description": "Short description of what the category covers.",
      "$label": "Display name: $name."
    }
  },
  {
    "type": "aspect",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "abstract",
    "description": "A qualitative or quantitative property attributed to any observation.",
    "ref": {
      "@person": {
        "description": "Person the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@country": {
        "description": "Country the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@location": {
        "description": "Location the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@product": {
        "description": "Product the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@event": {
        "description": "Event the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@project": {
        "description": "Project the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@task": {
        "description": "Task the aspect describes.",
        "relation": "subject",
        "verb": "has"
      },
      "@category": {
        "description": "Categories applied to the aspect.",
        "relation": "category",
        "verb": "has"
      }
    },
    "properties": {
      "$type": "Type: personal, financial, scientific, etc.",
      "$summary": "Max 100 words summary of the aspect.",
      "$label": "Display: ($type) $subject."
    }
  },
  {
    "type": "sentiment",
    "ontology_id": "https://airembr.com/world/default",
    "domain": "abstract",
    "description": "An expressed or inferred emotional valence toward an entity or topic.",
    "ref": {
      "@person": {
        "description": "Person evaluated, or expressing the sentiment.",
        "relation": "subject",
        "verb": "has"
      },
      "@organization": {
        "description": "Organization the sentiment targets.",
        "relation": "subject",
        "verb": "has"
      },
      "@country": {
        "description": "Country the sentiment targets.",
        "relation": "subject",
        "verb": "has"
      },
      "@product": {
        "description": "Product the sentiment targets.",
        "relation": "subject",
        "verb": "has"
      },
      "@event": {
        "description": "Event the sentiment targets.",
        "relation": "subject",
        "verb": "has"
      },
      "@document": {
        "description": "Document the sentiment targets or was expressed in.",
        "relation": "source",
        "verb": "has"
      },
      "@message": {
        "description": "Message expressing the sentiment.",
        "relation": "source",
        "verb": "has"
      },
      "@category": {
        "description": "Topic the sentiment is about.",
        "relation": "topic",
        "verb": "has"
      }
    },
    "properties": {
      "$polarity": "Overall polarity: positive, neutral, negative.",
      "$score": "Numeric score, e.g. -1.0 to 1.0.",
      "$label": "Display name: $polarity sentiment toward $subject."
    }
  }
]