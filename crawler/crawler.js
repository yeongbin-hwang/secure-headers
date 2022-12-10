const XLSX = require('xlsx');
const caniuse = require('caniuse-api');

class Crawler {
    constructor() {
        this.policies = [
            'cors',
            'contentsecuritypolicy',
            'contentsecuritypolicy2',
            'stricttransportsecurity',
            'x-frame-options',
            'feature-policy',
            'referrer-policy',
            'permissions-policy',
            'document-policy',
        ];
        this.policy_dict = {};
        this.browsers = [
            'Chrome for Android',
            'Firefox for Android',
            'QQ Browser',
            'UC Browser for Android',
            'Android Browser',
            'Baidu Browser',
            'Best Browser',
            'Chrome',
            'Edge',
            'Firefox',
            'IE',
            'IE Mobile',
            'Safari on iOS',
            'KaiOS Browser',
            'Opera Mini',
            'Opera Mobile',
            'Opera',
            'Safari',
            'Samsung Internet',
        ];
        this.browser_dict = {
            and_chr: 0,
            and_ff: 1,
            and_qq: 2,
            and_uc: 3,
            android: 4,
            baidu: 5,
            bb: 6,
            chrome: 7,
            edge: 8,
            firefox: 9,
            ie: 10,
            ie_mob: 11,
            ios_saf: 12,
            kaios: 13,
            op_mini: 14,
            op_mob: 15,
            opera: 16,
            safari: 17,
            samsung: 18,
        };
        this.browser_json = [];
        this.excelHandler = {
            getExcelFileName: function () {
                return 'log/version-check.xlsx';
            },
            getSheetName: function () {
                return 'browser version';
            },
        };
    }
    // collect the policy from caniuse
    run_crawl() {
        for (var policy of this.policies) {
            this.policy_dict[policy] = caniuse.getSupport(policy, true);
        }
        this.stable_versions = caniuse.getLatestStableBrowsers();
    }
    add_browser() {
        var i = 0;
        for (var broswer of this.browsers) {
            this.browser_json.push({'web broswer': broswer, 'stable version': this.stable_versions[i].split(' ')[1]});
            i += 1;
        }
    }
    beautify_features(feature) {
        feature = feature.replace(/,/g, '\n');
        feature = feature.replace(/[{}]/g, '');
        feature = feature.replace('"y":', 'Available: >= ');
        feature = feature.replace('"n":', 'Unavailable: <= ');
        feature = feature.replace('"a":', 'Partially support: <= ');
        feature = feature.replace('"x":', 'Prefixed: <= ');
        feature = feature.replace('"u":', 'Unknown: <= ');
        feature = feature.replace(/"[^naxu]*":[0-9.\n]*/g, '');
        return feature;
    }

    // convert the policy dict to json
    convert_dict_to_json() {
        this.add_browser();

        var i = 0;
        for (var policy of Object.values(this.policy_dict)) {
            for (var broswer_elem of Object.keys(policy)) {
                // ex) policy[broswer_elem] == {'y': 4}
                const feature = this.beautify_features(JSON.stringify(policy[broswer_elem]));
                this.browser_json[this.browser_dict[broswer_elem]][this.policies[i]] = feature;
            }
            i += 1;
        }
    }

    // convert json to excel
    convert_json_to_excel() {
        var wb = XLSX.utils.book_new();
        var newWorksheet = XLSX.utils.json_to_sheet(this.browser_json);
        XLSX.utils.book_append_sheet(wb, newWorksheet, this.excelHandler.getSheetName());
        XLSX.writeFile(wb, this.excelHandler.getExcelFileName(), {bookType: 'xlsx', type: 'binary'});
    }
}

crawl = new Crawler();
crawl.run_crawl();
crawl.convert_dict_to_json();
crawl.convert_json_to_excel();
