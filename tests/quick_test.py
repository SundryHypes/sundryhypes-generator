table = {
    'sub_table': {
        'content': 'sub_table_content'
    }
}

sub_table = table['sub_table']
sub_table['content'] = 'new_content'

print(table)