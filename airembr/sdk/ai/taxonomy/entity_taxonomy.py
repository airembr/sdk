taxonomy = [
    {
        "id": "Entity",
        "parent_id": None,
        "definition": "The root of the ontology - anything that exists and can be referred to in discourse",
        "examples": {}
    },
    {
        "id": "Continuant",
        "parent_id": "Entity",
        "definition": "Entities that persist through time while maintaining their identity - they exist in full at any time at which they exist at all",
        "examples": {}
    },
    {
        "id": "Occurrent",
        "parent_id": "Entity",
        "definition": "Entities that happen, unfold, or develop through time - they have temporal parts and are not wholly present at any single instant",
        "examples": {}
    },
    {
        "id": "Informational",
        "parent_id": "Entity",
        "definition": "Entities that depend on agents for their creation and existence - carriers or containers of information content",
        "examples": {}
    },
    {
        "id": "Property",
        "parent_id": "Entity",
        "definition": "Attributes, characteristics, or descriptors that describe or relate to entities - not standalone entities themselves",
        "examples": {}
    },
    {
        "id": "PhysicalObject",
        "parent_id": "Continuant",
        "definition": "A spatially extended entity that has mass, occupies physical space, and exists independently of other entities",
        "examples": {}
    },
    {
        "id": "NonPhysicalObject",
        "parent_id": "Continuant",
        "definition": "An entity that does not have spatial extension or mass but exists in social, legal, or conceptual reality",
        "examples": {}
    },
    {
        "id": "NaturalEntity",
        "parent_id": "PhysicalObject",
        "definition": "A physical object that exists in nature without human creation or significant modification",
        "examples": {
            "Plant": ["Oak Tree", "Watter Lily", "Bamboo", "Ivy", "Grass", "Flower"],
            "Animal": ["Wolf", "Zebra", "Dog", "Cat"],
            "Mineral": ["Gold", "silver", "Coal", "Soil", "Clay", "Sand", "Diamond"],
            "River": ["Amazon River", "Nile River", "Mississippi River", "Yangtze River", "Ganges River"],
            "Atmospheric phenomenon": ["Hurricane", "Rain", "Flood", "Snow", "Fog", "Wind", "Rainbow"],
            "Bacteria": ["E. Coli", "Salmonella", "Lactobacillus", "Staphylococcus", "Mycobacterium"],
            "Mountain": ["Mount Everest", "Mount Fuji", "Rocky Mountains", "Alps", "Himalayas"],
            "Ocean": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Southern Ocean"]
        }
    },
    {
        "id": "Artifact",
        "parent_id": "PhysicalObject",
        "definition": "A physical object created or significantly modified by intentional agent action for a specific purpose",
        "examples": {
            "Hammer": ["claw hammer", "mallet", "sledgehammer", "rubber hammer", "tack hammer"],
            "Computer": ["MacBook Pro", "Dell XPS", "ThinkPad", "iMac", "Surface Pro"],
            "House": ["Single-family home", "Townhouse", "Condo", "Cottage", "Mansion"],
            "Car": ["Toyota Camry", "Honda Civic", "Tesla Model 3", "Ford F-150", "BMW 3 Series"],
            "Painting": ["Mona Lisa", "The Starry Night", "The Scream", "Girl with a Pearl Earring", "American Gothic"],
            "Smartphone": ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12", "Sony Xperia"],
            "Bridge": ["Golden Gate Bridge", "Brooklyn Bridge", "Tower Bridge", "Sydney Harbour Bridge",
                       "Akashi Kaikyō Bridge"],
            "Book": ["Harry Potter series", "1984", "The Great Gatsby", "To Kill a Mockingbird", "Pride and Prejudice"],
            "Chair": ["Office chair", "Dining chair", "Rocking chair", "Bean bag", "Bar stool"],
            "Knife": ["Chef's knife", "Pocket knife", "Butter knife", "Scalpel", "Machete"]
        }
    },
    {
        "id": "Agent",
        "parent_id": "PhysicalObject",
        "definition": "An entity capable of intentional action - able to make decisions, pursue goals, and initiate changes in the world through will, cognition, or learned behavior",
        "examples": {
            "Person": ["John Smith", "Jane Doe", "Albert Einstein", "Marie Curie", "Elon Musk"],
            "AI System": ["GPT-4", "Claude", "DeepMind AlphaFold", "Tesla Autopilot", "IBM Watson"],
            "Animal": ["Border Collie", "Dolphin", "Chimpanzee", "Octopus", "Crow"],
            "Corporation": ["Apple Inc.", "Microsoft Corporation", "Tesla Inc.", "Amazon.com Inc.",
                            "Meta Platforms Inc."],
            "Robot": ["Boston Dynamics Spot", "Roomba", "Industrial robotic arm", "Amazon warehouse robot",
                      "Surgical robot"]
        }
    },
    {
        "id": "Location",
        "parent_id": "PhysicalObject",
        "definition": "A place in physical or geopolitical space - a spatial region that can be referred to by name or coordinates",
        "examples": {
            "City": ["New York City", "Tokyo", "London", "Paris", "Sydney"],
            "Country": ["United States", "Japan", "Germany", "Brazil", "Australia"],
            "Address": ["1600 Pennsylvania Avenue NW", "221B Baker Street", "350 Fifth Avenue", "1 Infinite Loop",
                        "Times Square"],
            "Mountain": ["Mount Everest", "Mount Kilimanjaro", "Mount Fuji", "K2", "Denali"],
            "Building": ["Empire State Building", "Eiffel Tower", "Burj Khalifa", "White House", "Statue of Liberty"],
            "Continent": ["North America", "Europe", "Asia", "Africa", "Australia"],
            "Region": ["Silicon Valley", "Pacific Northwest", "Middle East", "Scandinavia", "Caribbean"],
            "Landmark": ["Statue of Liberty", "Great Wall of China", "Pyramids of Giza", "Taj Mahal", "Colosseum"],
            "River": ["Amazon River", "Mississippi River", "Yangtze River", "Thames River", "Nile River"],
            "Island": ["Bermuda", "Cuba", "Hawaii", "Iceland", "Maldives"]
        }
    },
    {
        "id": "Organization",
        "parent_id": "NonPhysicalObject",
        "definition": "A structured group of agents with shared purpose, identity, and some form of governance or coordination",
        "examples": {
            "Company": ["Apple Computer Inc.", "Amazon", "Nike", "ASUS", "Google", ""],
            "Government": ["Federal Government", "Congress", "Supreme Court", "Executive Branch",
                           "Department of Defense"],
            "Committee": ["International Committee of the Red Cross"],
            "University": ["Harvard College", "Harvard Business School", "Harvard Law School",
                           "Harvard Medical School", "Harvard Kennedy School"],
            "Party": ["National Democratic Party", "Democratic National Committee", "State Democratic Party",
                      "Democratic Caucus", "Progressive Democrats"],
            "Catholic Church": ["Roman Catholic Church", "Vatican City", "Pope Francis", "Diocese", "Parish"]
        }
    },
    {
        "id": "Role",
        "parent_id": "NonPhysicalObject",
        "definition": "A function, position, or status that an agent can occupy, which defines expected behaviors, responsibilities, or rights within a context",
        "examples": {
            "Position": ["Chief Executive Officer of Apple", "CTO of Tesla", "CFO of Amazon", "Project Manger",
                         "Cashier", "Driver"],
            "Parent": ["Biological parent", "Foster parent", "Single parent", "Adoptive parent", "Co-parent"],
            "Citizen": ["U.S. citizen", "Naturalized citizen", "Dual citizen", "EU citizen", "Permanent resident"],
            "Doctor": ["General practitioner", "Surgeon", "Pediatrician", "Cardiologist", "Psychiatrist"],
            "Employee": ["Full-time employee", "Part-time employee", "Contractor", "Intern", "Freelancer"],
            "Friend": ["Best friend", "Childhood friend", "Work friend", "Online friend", "Mutual friend"],
            "Defendant": ["Criminal defendant", "Civil defendant", "Corporate defendant", "Government defendant",
                          " Juvenile defendant"],
            "Customer": ["Premium customer", "New customer", "Returning customer", "Enterprise customer",
                         "Retail customer"],
            "Child": ["Biological child", "Adopted child", "Stepchild", "Foster child", "Minor child"]
        }
    },
    {
        "id": "Concept",
        "parent_id": "NonPhysicalObject",
        "definition": "An abstract idea, category, or mental construct that exists in thought, language, or cultural discourse",
        "examples": {
            "Theory": ["Darwinian evolution", "Theory of Relativity", "Big Bang Theory", "Behaviorism",
                       "Marxism", "Keynesian Economics", "Utilitarianism", "Correspondence Theory of Truth",
                       "Plate Tectonics Theory"],
            "Democracy": ["Representative democracy", "Direct democracy", "Parliamentary democracy",
                          "Federal democracy", "Constitutional democracy"],
            "Justice": ["Social justice", "Criminal justice", "Distributive justice", "Retributive justice",
                        "Procedural justice"],
            "Physics": ["Quantum mechanics", "Thermodynamics", "Relativity", "Electromagnetism", "Classical mechanics"],
            "Religion": ["Christianity", "Islam", "Hinduism", "Buddhism", "Judaism"],
            "Freedom": ["Political freedom", "Economic freedom", "Freedom of speech", "Individual freedom",
                        "Personal freedom"],
            "Mathematics": ["Algebra", "Geometry", "Calculus", "Statistics", "Number theory"],
            "Language": ["English", "Spanish", "Mandarin", "Sign language", "Programming language"]
        }
    },
    {
        "id": "Rule",
        "parent_id": "NonPhysicalObject",
        "definition": "A normative, prescriptive, or logical constraint that governs behavior or reasoning - specifies what should be or what must follow",
        "examples": {
            "Law": ["Constitutional law", "Criminal law", "Civil law", "International law", "Contract law"],
            "Regulation": ["GDPR", "SEC regulations", "EPA regulations", "FDA regulations", "OSHA regulations"],
            "Policy": ["Employee handbook", "Code of conduct", "Data privacy policy", "Remote work policy",
                       "Expense policy"],
            "Axiom": ["Euclidean axioms", "Peano axioms", "ZFC axioms", "Logical axioms", "Mathematical axioms"],
            "Clause": ["Non-disclosure clause", "Indemnification clause", "Force majeure clause",
                       "Arbitration clause", "Termination clause"],
            "ToS": ["Facebook Terms of Service", "Google Terms of Service", "Apple Terms", "Netflix Terms",
                    "Spotify Terms"],
            "Protocol": ["HTTP protocol", "TCP/IP protocol", "SSH protocol", "Bluetooth protocol", "WebSocket protocol"]
        }
    },
    {
        "id": "Brand",
        "parent_id": "NonPhysicalObject",
        "definition": "A named identity representing perceived value, reputation, or association that distinguishes an entity in the marketplace or public mind",
        "examples": {
            "Apple": ["Apple Inc.", "Apple Watch", "Apple Music", "Apple TV", "Apple Pay"],
            "Nike": ["Nike Air Max", "Nike Jordan", "Nike Running", "Nike Training", "Nike SB"],
            "Coca-Cola": ["Coca-Cola Classic", "Diet Coke", "Coca-Cola Zero", "Cherry Coke", "Coca-Cola Light"],
            "Tesla": ["Tesla Model S", "Tesla Model 3", "Tesla Model X", "Tesla Model Y", "Tesla Cybertruck"],
            "iPhone": ["iPhone 15 Pro", "iPhone 15", "iPhone SE", "iPhone 14 Pro", "iPhone 14"],
            "Amazon Prime": ["Prime Video", "Prime Music", "Prime Shipping", "Prime Reading", "Prime Gaming"]
        }
    },
    {
        "id": "Software",
        "parent_id": "Technology",
        "definition": "Intangible programs, applications, and code that instruct computers to perform tasks - created by developers and existing as instructions rather than physical objects",
        "examples": {
            "Operating System": ["Windows 11", "macOS Sonoma", "Ubuntu 22.04", "Android 14", "iOS 17"],
            "Application": ["Microsoft Word", "Photoshop", "Chrome browser", "Spotify", "Slack"],
            "Programming Language": ["Python", "JavaScript", "C++", "Rust", "Go"],
            "Library/Framework": ["React", "TensorFlow", "NumPy", "Spring", "Django"],
            "Firmware": ["BIOS", "UEFI", "Router firmware", "IoT device firmware"],
            "Database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle DB"]
        }
    },
    {
        "id": "Event",
        "parent_id": "Occurrent",
        "definition": "A bounded occurrence in time - something that happens, typically with a defined beginning and end, which is a target for reference or documentation",
        "examples": {
            "Meeting": ["Team meeting", "Board meeting", "Client meeting", "One-on-one meeting", "Virtual meeting",
                        "Get together"],
            "Conference": ["Tech conference", "Medical conference", "Academic conference", "Business conference",
                           "Trade conference"],
            "War": ["World War II", "American Civil War", "Gulf War", "War in Afghanistan", "Ukraine War"],
            "Election": ["U.S. Presidential election", "Parliamentary election", "Primary election", "Runoff election",
                         "Referendum"],
            "Accident": ["Car accident", "Workplace accident", "Plane crash", "Train derailment",
                         "Industrial accident"],
            "Wedding": ["Religious wedding", "Civil wedding", "Destination wedding", "Virtual wedding",
                        "Renewal of vows"],
            "Product Launch": ["iPhone launch", "Product launch event", "Soft launch", "Global launch",
                               "Exclusive launch"],
            "Earthquake": ["2011 Tōhoku earthquake", "San Francisco earthquake", "Haiti earthquake", "Chile earthquake",
                           "Alaska earthquake"],
            "Graduation": ["High school graduation", "College graduation", "University graduation",
                           "Medical school graduation", "PhD graduation"],
            "Sport Event": ["World Cup Final 2022", "Premier League match", "Champions League Final", "Friendly match"]
        }
    },
    {
        "id": "Process",
        "parent_id": "Occurrent",
        "definition": "A sequence of actions, changes, or operations that unfold over time according to some pattern, method, or logic - repeatable or ongoing",
        "examples": {
            "Algorithm": ["Sorting algorithm", "Search algorithm", "Machine learning algorithm", "Encryption algorithm",
                          "Pathfinding algorithm"],
            "Workflow": ["Approval workflow", "Document workflow", "Manufacturing workflow",
                         "Customer onboarding workflow", "Bug tracking workflow"],
            "Metabolism": ["Cellular metabolism", "Basal metabolism", "Metabolic pathway", "Carbohydrate metabolism",
                           "Fat metabolism"],
            "Negotiation": ["Salary negotiation", "Contract negotiation", "Business negotiation",
                            "Diplomatic negotiation", "Peace negotiation"],
            "Manufacturing": ["Assembly line manufacturing", "3D printing manufacturing", "Lean manufacturing",
                              "Batch manufacturing", "Continuous manufacturing"],
            "Education": ["K-12 education", "Higher education", "Online education", "Vocational education",
                          "Special education"],
            "Photosynthesis": ["Light-dependent reactions", "Calvin cycle", "C3 photosynthesis", "C4 photosynthesis",
                               "CAM photosynthesis"]
        }
    },
    {
        "id": "Sport",
        "parent_id": "Process",
        "definition": "A structured physical or mental activity governed by rules, involving competition or play, typically undertaken for recreation, fitness, or professional purposes",
        "examples": {
            "Team Sport": ["Soccer", "Basketball", "Baseball", "American Football", "Hockey", "Volleyball"],
            "Individual Sport": ["Tennis", "Golf", "Boxing", "Swimming", "Track and Field", "Martial Arts"],
            "Motorsport": ["Formula 1", "NASCAR", "MotoGP", "Rally racing", "IndyCar"],
            "Water Sport": ["Surfing", "Sailing", "Rowing", "Canoeing", "Scuba diving"],
            "Winter Sport": ["Skiing", "Snowboarding", "Figure skating", "Ice hockey", "Bobsleigh"]
        }
    },
    {
        "id": "ProcessualEntity",
        "parent_id": "Occurrent",
        "definition": "A bounded process - a process with definite or conceptual boundaries, making it a reference target like an event but retaining internal structure",
        "examples": {
            "Project": ["Software development project", "Construction project", "Research project", "Marketing project",
                        "Event planning project"],
            "Campaign": ["Political campaign", "Marketing campaign", "Advertising campaign", "Fundraising campaign",
                         "Awareness campaign"],
            "Season": ["TV season", "Sports season", "Growing season", "School season", "Holiday season"],
            "Lifecycle": ["Product lifecycle", "Software lifecycle", "Human lifecycle", "Business lifecycle",
                          "Project lifecycle"],
            "Product Lifecycle": ["Introduction stage", "Growth stage", "Maturity stage", "Decline stage",
                                  "Product retirement"],
            "Treatment Program": ["Drug treatment program", "Rehabilitation program", "Mental health treatment program",
                                  "Physical therapy program", "Executive wellness program"],
            "Fiscal Year": ["FY2024", "FY2023", "Government fiscal year", "Corporate fiscal year",
                            "Academic fiscal year"]
        }
    },
    {
        "id": "Document",
        "parent_id": "Informational",
        "definition": "A structured carrier of recorded information, created by an agent, that persists through time and can be referenced, retrieved, or transmitted",
        "examples": {
            "Contract": ["Employment contract", "NDA", "Lease agreement", "Service agreement", "Sales contract"],
            "Book": ["Harry Potter and the Sorcerer's Stone", "1984", "The Great Gatsby", "To Kill a Mockingbird",
                     "The Catcher in the Rye"],
            "Email": ["Email with subject: Please contact me", "Meeting invitation", "Invoice email",
                      "Support ticket email", "Newsletter email"],
            "Law": ["GDPR", "HIPAA", "International Law", "Constitutional Law", "Criminal Law"],
            "Dataset": ["Census data", "Stock market data", "Climate data", "Medical records dataset",
                        "User behavior dataset"],
            "Invoice": ["Product invoice", "Service invoice", "Proforma invoice", "Recurring invoice",
                        "Commercial invoice"],
            "Report": ["Annual report", "Quarterly earnings report", "Audit report", "Research report",
                       "Status report"],
            "Certificate": ["Birth certificate", "Marriage certificate", "SSL certificate", "ISO certificate",
                            "Degree certificate"],
            "License": ["Driver's license", "Software license", "Business license", "Professional license",
                        "GPL license"]
        }
    },
    {
        "id": "Medium",
        "parent_id": "Informational",
        "definition": "A channel, format, or substrate through which information is communicated, stored, or transmitted - the means by which content is conveyed",
        "examples": {
            "Language": ["English", "JavaScript", "Python", "SQL", "HTML"],
            "USD": ["US Dollar", "USD banknotes", "USD coins", "USD wire transfer", "USD digital payment"],
            "Website": ["www.google.com", "www.wikipedia.org", "E-commerce website", "Blog website",
                        "Corporate website"],
            "PDF format": ["PDF/A", "PDF/X", "Encrypted PDF", "Fillable PDF", "PDF with digital signature"],
            "HTTP protocol": ["HTTP/1.1", "HTTP/2", "HTTPS", "HTTP headers", "HTTP methods"],
            "Television": ["Cable TV", "Satellite TV", "Streaming TV", "OTA TV", "Smart TV"],
            "Radio": ["AM radio", "FM radio", "Internet radio", "Satellite radio", "HD radio"]
        }
    },
    {
        "id": "Temporal",
        "parent_id": "Property",
        "definition": "A point or span in time - a property that describes when something occurs, exists, or has validity",
        "examples": {
            "Date": ["January 1, 2024", "December 25, 2023", "March 15, 2024", "July 4, 1776", "September 11, 2001"],
            "Era": ["Paleozoic Era", "Industrial Era", "Post-war Era", "Digital Era", "Information Era"],
            "Deadline": ["Q4 deadline", "Grant deadline", "Tax deadline", "Submission deadline", "Project deadline"],
            "Fiscal Year": ["FY2024", "FY2025", "Government fiscal year", "Academic fiscal year",
                            "Corporate fiscal year"],
            "Timestamp": ["Unix timestamp", "ISO 8601 timestamp", "UTC timestamp", "Local timestamp",
                          "Server timestamp"],
            "Timezone": ["UTC", "EST", "PST", "GMT", "JST"],
            "Quarter": ["Q1", "Q2", "Q3", "Q4", "Fiscal quarter"],
            "AirQualityMetric": ["AQI", "PM2.5", "PM10", "Ozone", "CO"]
        }
    },
    {
        "id": "Quantity",
        "parent_id": "Property",
        "definition": "A measurable or countable value representing magnitude, amount, or degree - a property that can be expressed with a unit",
        "examples": {
            "Price": ["$19.99", "$1,000,000", "€50", "¥10000", "$4.50/gallon"],
            "Distance": ["10 miles", "100 kilometers", "5 meters", "1,000 feet", "2 light-years"],
            "Duration": ["2 hours", "30 minutes", "1 week", "90 days", "25 years"],
            "Percentage": ["50%", "99.9%", "25.5%", "100%", "0.01%"],
            "Score": ["98/100", "4.0 GPA", "1500 SAT", "850 FICO", "9/10 rating"],
            "Population": ["8 billion", "331 million", "10 thousands"]
        }
    },
    {
        "id": "Relationship",
        "parent_id": "Property",
        "definition": "A named connection, association, or link between two or more entities - describes how entities relate to each other",
        "examples": {
            "Ownership": ["Home ownership", "Stock ownership", "Intellectual property ownership", "Vehicle ownership",
                          "Business ownership"],
            "Membership": ["Club membership", "Professional membership", "Subscription membership",
                           "Employee membership", "Family membership"],
            "Partnership": ["Business partnership", "Strategic partnership", "Marriage partnership",
                            "Research partnership", "Public-private partnership"],
            "Causality": ["Root cause", "Contributing factor", "Direct cause", "Proximate cause", "Chain of causation"],
            "Employment": ["Full-time employment", "Contract employment", "Self-employment", "Part-time employment",
                           "Volunteer employment"],
            "Parent-Child": ["Biological parent-child", "Adoptive parent-child", "Foster parent-child",
                             "Step parent-child", "Legal parent-child"]
        }
    },
    {
        "id": "Technology",
        "parent_id": "Concept",
        "definition": "Applied knowledge, methods, or systems that enable capabilities or solve problems - the practical application of scientific or technical knowledge",
        "examples": {
            "AI Model": ["GPT-4", "Claude", "Llama", "PaLM", "Stable Diffusion"],
            "Internet": ["IPv4", "IPv6", "Wi-Fi", "5G", "Fiber optic internet"],
            "Electric Vehicle": ["Tesla Model 3", "Chevrolet Bolt", "Nissan Leaf", "Ford Mustang Mach-E", "Rivian R1T"],
            "Vaccine": ["COVID-19 vaccine", "Flu vaccine", "Polio vaccine", "HPV vaccine", "Hepatitis B vaccine"],
            "GPS": ["Google Maps", "Waze", "Garmin", "TomTom", "Apple Maps"],
            "Blockchain": ["Bitcoin blockchain", "Ethereum", "Hyperledger", "Solana", "Cardano"],
            "IoT": ["Smart thermostat", "Connected car", "Wearable fitness tracker", "Smart home hub",
                    "Industrial sensor network"],
            "Robotics": ["Industrial robot", "Medical robot", "Warehouse robot", "Agricultural robot", "Humanoid robot"]
        }
    },
    {
        "id": "Transportation",
        "parent_id": "Process",
        "definition": "The process of moving people, goods, or information from one location to another through various means",
        "examples": {
            "Freight transportation": ["Container shipping", "Bulk cargo transport", "Rail freight", "Truck freight",
                                       "Intermodal freight"],
            "Public transit": ["Subway", "Bus", "Tram", "Light rail", "Commuter rail"],
            "Air travel": ["Commercial flight", "Private jet", "Charter flight", "Cargo flight", "Military flight"],
            "Shipping": ["Ocean shipping", "River shipping", "Coastal shipping", "Package shipping",
                         "Express shipping"],
            "Commuting": ["Daily commute", "Reverse commute", "Carpool", "Bike commuting", "Remote commuting"],
            "Logistics": ["Supply chain logistics", "Reverse logistics", "Third-party logistics",
                          "Cold chain logistics", "Last-mile delivery"]
        }
    },
    {
        "id": "TransportationInfrastructure",
        "parent_id": "Artifact",
        "definition": "Physical infrastructure and facilities that enable transportation - the built environment for moving people and goods",
        "examples": {
            "Highway": ["Interstate highway", "Freeway", "Expressway", "Toll highway", "Highway 101"],
            "Railway": ["High-speed rail", "Metro rail", "Light rail", "Freight rail", "Heritage railway"],
            "Airport": ["International airport", "Domestic airport", "Regional airport", "Cargo airport",
                        "Private airport"],
            "Seaport": ["Container port", "Bulk cargo port", "Fishing port", "Marina", "Cruise port"],
            "Bridge": ["Suspension bridge", "Arch bridge", "Cable-stayed bridge", "Drawbridge", "Covered bridge"],
            "Tunnel": ["Road tunnel", "Rail tunnel", "Pedestrian tunnel", "Utility tunnel", "Underwater tunnel"],
            "Bus stop": ["Urban bus stop", "Highway rest stop", "School bus stop", "Park and ride", "Transit hub"],
            "Metro station": ["Underground station", "Elevated station", "Surface station", "Interchange station",
                              "Terminal station"]
        }
    },
    {
        "id": "TransportationSystem",
        "parent_id": "ProcessualEntity",
        "definition": "An integrated system of transportation infrastructure, vehicles, and management that enables coordinated movement",
        "examples": {
            "Intelligent Transportation System": ["Smart traffic management", "Connected vehicle system",
                                                  "Adaptive signal control", "Electronic toll collection",
                                                  "Real-time traffic monitoring"],
            "Public transit network": ["MTA NYC Transit", "London Underground", "Tokyo Metro", "Paris Métro",
                                       "Chicago CTA"],
            "Air traffic control system": ["En-route ATC", "Terminal ATC", "Airport tower", "Approach control",
                                           "Center ATC"],
            "Shipping route": ["Trans-Pacific route", "Trans-Atlantic route", "Northern Sea Route",
                               "Panama Canal route", "Suez Canal route"]
        }
    },
    {
        "id": "FinancialObligation",
        "parent_id": "NonPhysicalObject",
        "definition": "A legally binding duty to pay or deliver something of value",
        "examples": {
            "Tax": ["Income tax", "Property tax", "Sales tax", "Corporate tax"],
            "Fee": ["Tuition fee", "License fee", "Membership fee", "Processing fee"],
            "Fine": ["Parking fine", "Traffic ticket", "Tax penalty", "Legal fine"],
            "Toll": ["Highway toll", "Bridge toll", "Congestion charge", "Turnpike toll"],
            "Payable": ["Credit payable", "Cost", "Payment"],
            "Receivable": ["Credit receivable", "Income", "Payment"]
        }
    }
]
