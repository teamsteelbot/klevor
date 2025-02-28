import json


# Load the exported JSON data and filter labels containing the desired classes
def filter_classes(input_file_path, output_file_path, included_classes):
    # Load the exported JSON data
    with open(input_file_path, "r") as file:
        data = json.load(file)

    # Filter tasks containing the desired classes
    filtered_data = []
    for task in data:
        filtered_annotations = []
        for annotation in task.get("annotations", []):
            filtered_results = []
            for result in annotation.get("result", []):
                labels = result.get("value", {}).get("rectanglelabels", [])
                if any(label in included_classes for label in labels):
                   filtered_results.append(result)

            if filtered_results:
                filtered_annotations.append({**annotation, "result": filtered_results})

        if filtered_annotations:
            filtered_data.append({**task, "annotations": filtered_annotations})

    # Save the filtered data
    with open(output_file_path, "w") as file:
        json.dump(filtered_data, file, indent=4)

    print(f"Filtered data with selected classes saved to {output_file_path}")
