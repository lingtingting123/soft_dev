import { Form, Formik, Field } from 'formik'
// import React from 'react'
import React,{ useState } from 'react' // 修改 4/13
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from 'react-query'
import axios from 'axios'
import { FormErrors, TagsInput } from '../components'
import { useArticleQuery } from '../hooks'

function Editor() {
  const navigate = useNavigate()
  const articleQuery = useArticleQuery()
  const queryClient = useQueryClient()
  const article = articleQuery?.data?.article || {}
  const { slug } = article

  const [titleError, setTitleError] = useState("");//修改 4/13
  //  4/13检查标题
  async function checkTitleExists(title) {
    if (!title) return;
  
    try {
      const response = await axios.get(`/api/articles/check-title?title=${encodeURIComponent(title)}`);
  
      if (response.data.exists) {  // 确保后端返回 { "exists": true/false }
        setTitleError("该文章标题已存在，请更换标题");
      } else {
        setTitleError("");
      }
    } catch (err) {
      console.error("检查标题失败", err);
    }
  }
  
  async function onSubmit(values, { setErrors }) {
    if (titleError) {
      console.warn("标题已存在，禁止提交");
      return;
    }  //  4/13
    
    console.log("提交的数据:", values); // 确保 `tagList` 不是空的

    try {
      const { data } = await axios[slug ? 'put' : 'post'](`/articles${slug ? `/${slug}` : ''}`, { article: values })

      if (slug) {
        queryClient.invalidateQueries(`/articles/${slug}`)
      } else {
        queryClient.invalidateQueries('/articles')
      }

      navigate(`/article/${data?.article?.slug}`)
    } catch (error) {
      const { status, data } = error.response

      if (status === 400) {  
        setTitleError(data.error || "文章提交失败，请检查输入内容");
      } else if (status === 422) {
        setErrors(data.errors);
      } else {
        console.error("提交失败:", error);
      }  // 4/13
    }
  }

  return (
    <div className="editor-page">
      <div className="container page">
        <div className="row">
          <div className="col-md-10 offset-md-1 col-xs-12">
            <Formik
              onSubmit={onSubmit}
              initialValues={{
                title: article?.title || '',
                description: article?.description || '',
                body: article?.body || '',
                tagList: article?.tagList || [],
                scheduledAt: article?.scheduledAt || '', // 添加 scheduledAt 初始值
              }}
              enableReinitialize
            >
              {({ isSubmitting }) => (
                <>
                  <FormErrors />
                  <Form>
                    <fieldset disabled={isSubmitting}>
                      <fieldset className="form-group">
                        <Field
                          name="title"
                          type="text"
                          className="form-control form-control-lg"
                          placeholder="Article Title"
                          onBlur={(e) => checkTitleExists(e.target.value)} // 失去焦点时检查标题 4/13
                        />
                         {titleError && <p style={{ color: "red" }}>{titleError}</p>}
                      </fieldset>
                      <fieldset className="form-group">
                        <Field
                          name="description"
                          type="text"
                          className="form-control"
                          placeholder="What's this article about?"
                        />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field
                          name="body"
                          as="textarea"
                          className="form-control"
                          rows={8}
                          placeholder="Write your article (in markdown)"
                        />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field name="tagList" component={TagsInput} />
                      </fieldset>

                      {/* 添加定时发送输入框 3/28 */}
                      <fieldset className="form-group">
                        <label>Schedule Publish Date</label>
                        <Field name="scheduledAt" type="datetime-local" className="form-control" />
                      </fieldset>

                      <button className="btn btn-lg pull-xs-right btn-primary" type="submit">
                        Publish Article
                      </button>
                    </fieldset>
                  </Form>
                </>
              )}
            </Formik>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Editor
