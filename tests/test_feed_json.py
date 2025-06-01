import json
import xml.etree.ElementTree as ET


def xml_to_json_items(xml_str):
    root = ET.fromstring(xml_str)
    items = []
    for item in root.findall('.//item'):
        data = {child.tag: (child.text or '') for child in item}
        items.append(data)
    return json.dumps(items)


def test_xml_to_json_items():
    xml = '<rss><channel><item><title>A</title><link>B</link></item></channel></rss>'
    js = xml_to_json_items(xml)
    data = json.loads(js)
    assert data[0]['title'] == 'A'
    assert data[0]['link'] == 'B'
