servers = {'pro': 'xg.mediportal.com.cn',
           'pre': 'pre.mediportal.com.cn',
           'test': 'test.mediportal.com.cn'}

interfaces = {
    'basedata_read':
        {
            'interface':
                {
                    'getCatagory':
                        {
                            'desc': '获取基础资料所有类别',
                            'method': 'GET',
                            'url': '/open-api/drugorg/openapi/default/category',
                            'params': ['orgId', 'appKey', 'nonce', 'time', 'sign']
                        },
                    'getEntry':
                        {
                            'desc': '获取基础资料条目',
                            'method': 'GET',
                            'url': '/open-api/drugorg/openapi/default/entry',
                            'params': ['orgId', 'appKey', 'nonce', 'time', 'sign']
                        }
                },
            'api_key':
                {
                    'pro': '',
                    'pre': '',
                    'test': ''
                },
            'api_secret':
                {
                    'pro': '',
                    'pre': '',
                    'test': ''
                }
        },
    'organization_read':
        {

        },
    'crm_read':
        {
            'interface':
                {
                    'queryHospitalData':
                        {
                            'desc': '查询药企圈医院数据',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryHospitalData',
                            'params': ['appKey', 'nonce', 'time', 'sign','timeStamp','pageIndex','pageSize'],
                            'output': ['data','pageData']
                        },
                    'queryCompanyHospitalData':
                        {
                            'desc': '查询企业自行创建的医院数据',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryCompanyHospitalData',
                            'params': ['appKey', 'nonce', 'time', 'sign','timeStamp','companyId','pageIndex','pageSize'],
                            'output': ['data','pageData']
                        },
                    'queryCompanyCustomerData':
                        {
                            'desc': '查询企业客户数据',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryCompanyCustomerData',
                            'params': ['appKey', 'nonce', 'time', 'sign','timeStamp','companyId','pageIndex','pageSize'],
                            'output': ['data','pageData']
                        },
                    'queryFriendsByOpenId':
                        {
                            'desc': '查询客户与员工的好友关系',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryFriendsByOpenId',
                            'params': ['appKey', 'nonce', 'time', 'sign','openId','companyId'],
                            'output': ['data']
                        },
                    'queryFriendsByCustomerId':
                        {
                            'desc': '查询员工与客户的好友关系',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryFriendsByCustomerId',
                            'params': ['appKey', 'nonce', 'time', 'sign','customerId','companyId'],
                            'output': ['data']
                        },
                    'queryCustomerLastLoginTime':
                        {
                            'desc': '查询客户最近登录医生圈的时间',
                            'method': 'GET',
                            'url': '/open-api/drugorg/crm/open/queryCustomerLastLoginTime',
                            'params': ['appKey', 'nonce', 'time', 'sign','timeStamp','companyId'],
                            'output': ['data']
                        }
                },
            'api_key':
                {
                    'pro': '',
                    'pre': '',
                    'test': '3b00bfb4c77b41e9b7d6eec2180855c6'
                },
            'api_secret':
                {
                    'pro': '',
                    'pre': '',
                    'test': 'f88c8e674995445889613eb9b47fc940fxr7k710'
                }
        },
    'crm_write':
        {
            'interface':
                {
                    'addResponsibility':
                        {
                            'desc': '添加员工与医院及品种的分管关系',
                            'method': 'POST',
                            'url': '/open-api/drugorg/crm/open/addResponsibility',
                            'params': ['appKey', 'nonce', 'time', 'sign'],
                            'body': True
                        },
                    'deleteResponsibility':
                        {
                            'desc': '删除员工与医院及品种的分管关系',
                            'method': 'POST',
                            'url': '/open-api/drugorg/crm/open/deleteResponsibility',
                            'params': ['appKey', 'nonce', 'time', 'sign'],
                            'body': True
                        },
                    'clearResponsibilitiesByOpenId':
                        {
                            'desc': '清除员工的所有分管关系',
                            'method': 'POST',
                            'url': '/open-api/drugorg/crm/open/clearResponsibilitiesByOpenId',
                            'params': ['appKey', 'nonce', 'time', 'sign']
                        }
                },
            'api_key':
                {
                    'pro': '',
                    'pre': '',
                    'test': '830efb764927426ea874e7953dd43e1d'
                },
            'api_secret':
                {
                    'pro': '',
                    'pre': '',
                    'test': 'f88c8e674995445889613eb9b47fc940fxr7k706'
                }
        },
    'community':
        {

        }
}