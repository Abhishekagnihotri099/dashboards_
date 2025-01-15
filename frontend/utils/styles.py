def get_navigation_style():
    return """
        <style>
        .nav-container {
            display: flex;
            justify-content: space-between;
            padding: 1rem;
            background-color: #0078D4;
            margin-bottom: 2rem;
        }
        .nav-item {
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 5px;
        }
        .nav-item:hover {
            background-color: #005A9E;
        }
        .nav-item.active {
            background-color: #005A9E;
        }
        </style>
    """