# rapidform-nepal-mm
For COVID-19 Global Hackathon

The data extraction code can be run with the following:
`docker-compose build && docker-compose run nepal`

That will build a docker image and run `main.py` which is hardcoded to extract data from nepal2.jpg. The logic for an image is as follows:
- use the google vision API for text detection on the image
- generate a new image file which is the image aligned with the template form. The alignment is done using `ANCHOR_TEXT` whose locations are found based on the google vision API json response
- rerun the new aligned image through the google vision API
- look for the `CHECKBOX_LABELS` text in the form to find the top left coordinate of each label
- once we know those coordinates, we can add the width of the label to get the top left coordinate of a checkbox
- for each grouping of checkboxes(gender, and each yes/no group), identify which checkbox has the most black and that's the checked value. If the difference among the checkboxes for a given group is too small, then conclude that no box was checked (and this probably should be manually confirmed)
- parse the handwritten text results from the google api
- combine with the checkbox results with the handwritten text answers and this is the form data
