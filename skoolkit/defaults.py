# -*- coding: utf-8 -*-

# Copyright 2014 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of SkoolKit.
#
# SkoolKit is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# SkoolKit is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# SkoolKit. If not, see <http://www.gnu.org/licenses/>.

REF_FILE = """
[Info]
Copyright=
Created=Created using <a class="link" href="http://pyskool.ca/?page_id=177">SkoolKit</a> $VERSION.
Release=

[Template:head]
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>{Game}: {title}</title>
{t_stylesheets}
{t_javascripts}
</head>

[Template:stylesheet]
<link rel="stylesheet" type="text/css" href="{href}" />

[Template:javascript]
<script type="text/javascript" src="{src}"></script>

[Template:footer]
<div class="footer">
<div class="release">{Info[Release]}</div>
<div class="copyright">{Info[Copyright]}</div>
<div class="created">{Info[Created]}</div>
</div>

[Template:index_section]
<div class="headerText">{header}</div>
{t_link_list}

[Template:index]
{t_head}
<body class="main">
<table class="header">
<tr>
<td class="headerText">{TitlePrefix}</td>
<td class="headerLogo">{Logo}</td>
<td class="headerText">{TitleSuffix}</td>
</tr>
</table>
{t_index_sections}
{t_footer}
</body>
</html>

[Template:asm_entry]
{t_head}
<body class="disassembly">
{t_header}
{t_prev_next}
<div class="description">{entry_title}</div>
{t_disassembly}
{t_prev_next}
{t_footer}
</body>
</html>

[Template:header]
<table class="header">
<tr>
<td class="headerLogo"><a class="link" href="{href}">{Logo}</a></td>
<td class="headerText">{header}</td>
</tr>
</table>

[Template:routine_title]
Routine at {address}{label_suffix}

[Template:routine_header]
Routines

[Template:gsb_title]
Game status buffer entry at {address}{label_suffix}

[Template:gsb_header]
Game status buffer

[Template:data_title]
Data at {address}{label_suffix}

[Template:data_header]
Data

[Template:unused_title]
Unused RAM at {address}{label_suffix}

[Template:unused_header]
Unused

[Template:prev_next]
<table class="prevNext">
<tr>
<td class="prev">{t_prev}</td>
<td class="up">{t_up}</td>
<td class="next">{t_next}</td>
</tr>
</table>

[Template:prev]
Prev: <a class="link" href="{href}">{text}</a>

[Template:up]
Up: <a class="link" href="{href}">Map</a>

[Template:next]
Next: <a class="link" href="{href}">{text}</a>

[Template:disassembly]
<table class="{table_class}">
<tr>
<td class="routineComment" colspan="{colspan}">
<div class="details">
{entry_details}
</div>
{t_input}
{t_output}
</td>
</tr>
{t_instructions}
</table>

[Template:anchor]
<a name="{anchor}"></a>

[Template:entry_comment]
<tr>
<td class="routineComment" colspan="{colspan}">
{t_anchor}
<div class="comments">
{t_paragraphs}
</div>
</td>
</tr>

[Template:input]
<table class="input">
{t_registers_header}
{t_registers}
</table>

[Template:output]
<table class="output">
{t_registers_header}
{t_registers}
</table>

[Template:registers_header]
<tr>
<th colspan="2">{header}</th>
</tr>

[Template:register]
<tr>
<td class="register">{register.name}</td>
<td class="registerContents">{register.description}</td>
</tr>

[Template:instruction]
<tr>
{t_asm_label}
<td class="{class}">{t_anchor}{address}</td>
<td class="instruction">{instruction}</td>
{t_instruction_comment}
</tr>

[Template:instruction_comment]
<td class="{class}"{rowspan}>{comment}</td>

[Template:asm_label]
<td class="asmLabel">{label}</td>

[Template:paragraph]
<div class="paragraph">
{paragraph}
</div>

[Template:link_list]
<ul class="{list_class}">
{t_link_list_items}
</ul>

[Template:link_list_item]
<li><a class="link" href="{href}">{link_text}</a>{other_text}</li>

[Template:link]
<a class="link" href="{href}">{link_text}</a>

[Template:map]
{t_head}
<body class="map">
{t_header}
{t_map_intro}
<table class="map">
<tr>
{t_map_page_byte_header}
<th>Address</th>
<th>Description</th>
</tr>
{t_map_entries}
</table>
{t_footer}
</body>
</html>

[Template:map_intro]
<div class="mapIntro">{intro}</div>

[Template:map_entry]
<tr>
{t_map_page_byte}
<td class="{class}"><a class="link" name="{entry.address}" href="{href}">{entry.addr_str}</a></td>
<td class="{desc_class}">{entry.title}</td>
</tr>

[Template:map_page_byte_header]
<th>Page</th>
<th>Byte</th>

[Template:map_page_byte]
<td class="mapPage">{page}</td>
<td class="mapByte">{byte}</td>

[Template:map_unused_desc]
Unused ({entry.size} byte{suffix})

[Template:GameStatusBuffer]
{t_head}
<body class="gbuffer">
{t_header}
<table class="gbuffer">
<tr>
<th>Address</th>
<th>Length</th>
<th>Purpose</th>
</tr>
{t_gsb_entries}
</table>
{t_footer}
</body>
</html>

[Template:gsb_entry]
<tr>
<td class="gbufAddress"><a name="{entry[location]}" class="link" href="{entry[url]}">{entry[address]}</a></td>
<td class="gbufLength">{entry[size]}</td>
<td class="gbufDesc">
<div class="gbufDesc">{entry[title]}</div>
<div class="gbufDetails">
{entry[description]}
</div>
</td>
</tr>

[Template:Changelog]
{t_head}
<body class="changelog">
{t_header}
{t_contents_list}
{t_changelog_entries}
{t_footer}
</body>
</html>

[Template:contents_list]
<ul class="linkList">
{t_contents_list_items}
</ul>

[Template:contents_list_item]
<li><a class="link" href="{item[url]}">{item[title]}</a></li>

[Template:changelog_entry]
<div>{t_anchor}</div>
<div class="changelog changelog{changelog_num}">
<div class="changelogTitle">{entry[title]}</div>
<div class="changelogDesc">{entry[description]}</div>
{t_changelog_item_list}
</div>

[Template:changelog_item_list]
<ul class="changelog{indent}">
{t_changelog_items}
</ul>

[Template:changelog_item]
<li>{item}</li>

[Template:Pokes]
{t_head}
<body class="pokes">
{t_header}
{t_contents_list}
{t_boxes}
{t_footer}
</body>
</html>

[Template:Bugs]
{t_head}
<body class="bugs">
{t_header}
{t_contents_list}
{t_boxes}
{t_footer}
</body>
</html>

[Template:Facts]
{t_head}
<body class="facts">
{t_header}
{t_contents_list}
{t_boxes}
{t_footer}
</body>
</html>

[Template:Glossary]
{t_head}
<body class="glossary">
{t_header}
{t_contents_list}
{t_boxes}
{t_footer}
</body>
</html>

[Template:GraphicGlitches]
{t_head}
<body class="graphics">
{t_header}
{t_contents_list}
{t_boxes}
{t_footer}
</body>
</html>

[Template:Graphics]
{t_head}
<body class="graphics">
{t_header}
{Graphics}
{t_footer}
</body>
</html>

[Template:box]
<div>{t_anchor}</div>
<div class="box box{box_num}">
<div class="boxTitle">{title}</div>
{contents}
</div>
""".lstrip()
