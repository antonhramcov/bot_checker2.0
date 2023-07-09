def convert(s: list):
    out_string = ['']
    for i in range(len(s)):
        out_string[-1] += f'<b>{i+1}. Line: {s[i]["line"]}</b>;\n'
        out_string[-1] += 'sources: '
        if len(s[i]['sources']) == 0:
            out_string[-1] += 'unknown; '
        else:
            for j in range(len(s[i]['sources'])-1):
                out_string[-1] += s[i]['sources'][j]+', '
            out_string[-1] += s[i]['sources'][-1]+'; '
        out_string[-1] += f'\nemail_only: {s[i]["email_only"]};\n'
        out_string[-1] += f'last_breach: {s[i]["last_breach"]}\n\n'
        if len(out_string[-1])>3800:
            out_string.append('')
    return out_string

def convert_for_bitch(s: list):
    out_string = ['']
    for i in range(len(s)):
        sleep_strings = s[i]["line"].split(':')
        if len(sleep_strings[-1])>4:
            sleep_strings[-1] = sleep_strings[-1][:2]+'*'*(len(sleep_strings[-1])-4)+sleep_strings[-1][-2:]
        out_string[-1] += f'<b>{i + 1}. Line: {sleep_strings[0]}:{sleep_strings[-1]}</b>;\n'
        out_string[-1] += 'sources: '
        if len(s[i]['sources']) == 0:
            out_string[-1] += 'unknown; '
        else:
            for j in range(len(s[i]['sources']) - 1):
                out_string[-1] += s[i]['sources'][j] + ', '
            out_string[-1] += s[i]['sources'][-1] + '; '
        out_string[-1] += f'\nemail_only: {s[i]["email_only"]};\n'
        out_string[-1] += f'last_breach: {s[i]["last_breach"]}\n\n'
        if len(out_string[-1]) > 3800:
            out_string.append('')
    return out_string


